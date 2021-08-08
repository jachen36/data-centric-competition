# standard library
import sys
from pathlib import Path
from typing import Tuple, Union

# third party
import tensorflow as tf


def train_model(
    user_data: Union[str, Path], test_data: Union[str, Path], short_run: bool = False
) -> Tuple[float, float]:
    """ "Run competition model on your dataset

    args:
        user_data : str, Path
            Path where your train and val folder is located where each symbol are in their individual folder
        test_data : str, Path
            where label_book is located
        short_run : bool
            wheather to run a few epochs or the full 100 epochs set by competition

    return:
        loss, acc from validation
    """

    user_data = Path(user_data)
    # this can be the label book, or any other test set you create
    test_data = Path(test_data)

    ### DO NOT MODIFY BELOW THIS LINE, THIS IS THE FIXED MODEL ###
    batch_size = 8
    tf.random.set_seed(123)
    epochs = 5 if short_run else 100

    train = tf.keras.preprocessing.image_dataset_from_directory(
        user_data / "train",
        labels="inferred",
        label_mode="categorical",
        class_names=["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"],
        shuffle=True,
        seed=123,
        batch_size=batch_size,
        image_size=(32, 32),
    )

    valid = tf.keras.preprocessing.image_dataset_from_directory(
        user_data / "val",
        labels="inferred",
        label_mode="categorical",
        class_names=["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"],
        shuffle=True,
        seed=123,
        batch_size=batch_size,
        image_size=(32, 32),
    )

    total_length = ((train.cardinality() + valid.cardinality()) * batch_size).numpy()
    if total_length > 10_000:
        print(f"Dataset size larger than 10,000. Got {total_length} examples")
        sys.exit()

    test = tf.keras.preprocessing.image_dataset_from_directory(
        test_data,
        labels="inferred",
        label_mode="categorical",
        class_names=["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"],
        shuffle=False,
        seed=123,
        batch_size=batch_size,
        image_size=(32, 32),
    )

    base_model = tf.keras.applications.ResNet50(
        input_shape=(32, 32, 3), include_top=False, weights=None
    )
    base_model = tf.keras.Model(
        base_model.inputs, outputs=[base_model.get_layer("conv2_block3_out").output]
    )

    inputs = tf.keras.Input(shape=(32, 32, 3))
    x = tf.keras.applications.resnet.preprocess_input(inputs)
    x = base_model(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(10)(x)
    model = tf.keras.Model(inputs, x)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(lr=0.0001),
        loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )
    model.summary()
    loss_0, acc_0 = model.evaluate(valid)
    print(f"loss {loss_0}, acc {acc_0}")

    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        "best_model",
        monitor="val_accuracy",
        mode="max",
        save_best_only=True,
        save_weights_only=True,
    )

    _ = model.fit(train, validation_data=valid, epochs=epochs, callbacks=[checkpoint])

    model.load_weights("best_model")

    loss, acc = model.evaluate(valid)
    test_loss, test_acc = model.evaluate(test)

    print(f"final loss {loss}, final acc {acc}")
    print(f"test loss {test_loss}, test acc {test_acc}")
    return loss, acc
