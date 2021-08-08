import shutil
from pathlib import Path
from typing import Dict, List, Union

import pandas as pd


def validation(annot_dict) -> bool:
    """Check if annotations meet expecations

    args:
        annot_dict : dict
            parsed json of annotations.json from superannotation

    return:
        boolean

    """

    # metadata that we are interested
    key_skips = ["___sa_version___"]
    valid_images = [".png"]

    for idx, (key, value) in enumerate(annot_dict.items(), 0):

        if key in key_skips:
            continue

        header = f"{idx}::{key}"

        assert (
            Path(key).suffix in valid_images
        ), f"{header} Unexpected image file extension, add new extension if true"
        assert "thmb" not in key, f"{header} Found SuperAnnotate thumbnail images"

        assert (
            value["metadata"]["status"] != "Not started"
        ), f"{header}: has not been started"

        bboxes = value["instances"]
        assert len(bboxes) == 1, f"{header}: Each image should only have 1 symbol"

        attributes = bboxes[0]["attributes"]
        symbol = [attr for attr in attributes if attr["groupId"] == 1]
        assert len(symbol) == 1, f"{header}: Missing symbol label"
        assert symbol[0]["id"] in range(
            1, 11
        ), f"{header}: Symbol is not within 1 to 10"

    return True


def get_image_idx(annot_dict: dict, name: str) -> int:
    """Return the idx of an image sorted by SuperAnnotate

    args:
        annot_dict : dict
            parsed annotations.json
        name : str
            filename of the image of interest

    return:
        int
    """

    assert name in annot_dict, "Image not found"

    for idx, (key, value) in enumerate(annot_dict.items(), 0):
        if name == key:
            return idx


def get_original_labels(source_dir: Union[str, Path]) -> pd.DataFrame:
    """Get original images' train/val split and symbol labeling

    args:
        source_dir : str, Path
            the directory for where

    return:
        list[dict]
    """
    source_dir = Path(source_dir)

    collections = []
    for image_pt in source_dir.rglob("*.png"):
        entry = {
            "image": image_pt.name,
            "org_symbol": image_pt.parent.name,
            "org_source": image_pt.parent.parent.name,
        }
        collections.append(entry)

    return pd.DataFrame(collections)


def stratified_train_test_split(
    df: pd.DataFrame, by: Union[str, List[str]], test_pct: float = 0.3, random_state=42
) -> list:
    """Stratified train and test split based one or more column

    args:
        df : pd.Dataframe
            dataframe for which you want to split
        by : str, list
            what columns to stratified by
        test_pct : float
            percentage of samples in test
        random_state : int

    return
        list
            list for each row
    """

    tasks = ["train", "test"]
    stratified_split = (
        df.groupby(by, group_keys=False).apply(
            lambda x: pd.Series(tasks).sample(
                len(x),
                replace=True,
                weights=[1 - test_pct, test_pct],
                random_state=random_state,
            )
        )
    ).tolist()
    return stratified_split


def convert_annotation_to_dataframe(
    annot_dict: dict, class_mapping: dict = None
) -> pd.DataFrame:
    """Convert SuperAnnotate Json to dataframe

    args:
        annot_dict : dict
            parsed SuperAnnotate annotations.json
        class_mapping : dict
            parsed SuperAnnotate classes.json


    returns
        pd.DataFrame
            where each image is a row and attributes are columns
    """
    validation(annot_dict)

    annot_dict.pop("___sa_version___", None)

    collections = []
    for idx, (key, value) in enumerate(annot_dict.items(), 1):
        entry = {
            "idx": idx,
            "image": key,
        }
        attributes = {
            attribute["groupId"]: attribute["id"]
            for attribute in value["instances"][0]["attributes"]
        }
        entry.update(attributes)

        collections.append(entry)

    collections = pd.DataFrame(collections)

    if class_mapping:

        class_mapping = class_mapping[0]["attribute_groups"]
        rename_columns = {c["id"]: c["name"] for c in class_mapping}
        collections.rename(columns=rename_columns, inplace=True)

        for c in class_mapping:
            value_mapping = {v["id"]: v["name"] for v in c["attributes"]}
            collections[c["name"]] = collections[c["name"]].map(value_mapping)

    return collections


def copy_group_to_dir(
    df: pd.DataFrame,
    source_dir: Union[str, Path],
    dest_dir: Union[str, Path],
    group: Union[str, List[str]],
    prefix_image: str = None,
) -> List[Dict[str, str]]:
    """Group images together by copying image into separate directory based on one
        attribute and its value

    args:
        df : pd.DataFrame
            each image as a row with features as column
        source_dir : str, Path
            where all the images are located in a flatten format
        dest_dir : str, Path
            where to copy the images to
        group : str, List[str]
            what feature's value to break the groups into based. create nested directory
        prefix_image : str
            column to to prefix image filename

    returns
        list of images that doesn't exist in either the dataframe or source_dir

    notes:
    nan values are dropped so if you want them, fillnan with a value like "none"
    This makes it easier to find odd ones when group of images are placed together and
    viewed in a grid.
    """
    source_dir = Path(source_dir)  # has to be the flatten
    source_images = {i.name: i for i in list(source_dir.glob("*.png"))}
    assert len(source_images) > 0, f"No images found. Could be wrong path: {source_dir}"
    dest_dir = Path(dest_dir)

    unknown_images = list(set(df.image) - set(source_images.keys())) + list(
        set(source_images.keys()) - set(df.image)
    )

    df = df.dropna(subset=group).copy()
    for name, group in df.groupby(group):

        dest = dest_dir.joinpath(*name)
        dest.mkdir(parents=True, exist_ok=True)

        for row in group.itertuples():
            org_image_path = source_images.get(row.image, None)

            if org_image_path:
                if prefix_image:
                    copy_image_name = "_".join([getattr(row, prefix_image), row.image])
                else:
                    copy_image_name = row.image
                shutil.copy(org_image_path, dest / copy_image_name)

    return unknown_images
