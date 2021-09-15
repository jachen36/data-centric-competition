# Data-Centric Ai Competition

First ever type of data science competition where the only focus is on the data rather than data plus modeling. Overall the competition is similar to [Kaggle](https://www.kaggle.com/) where teams are ranked based on how well the model perform on a private held out data set; however, the difference is that the model is held static and every team will need to be creative in how they clean, feature engineer, or augment the data inorder to improve the model performance. This is a new trend that Andrew Ng is starting because high-performance model architectures are widely available, while approaches to engineering datsets have lagged.

[Data-centric Ai](https://https-deeplearning-ai.github.io/data-centric-comp/) Competition landing page.

# Summary of My Approach

Due to the limited amount of time I had, I wasn't able to try much before it ended. Also because the leaderboard takes a long time to update after submission, the last few tried failed to make it to the leaderboard; therefore, I cannot tell if the augmentation experiment was fruitfull.

1. Consistent labeling by documenting a guide on how to label. [labeling-guide](labeling-guide.md)
1. Augmentations to add variety to the training dataset and make model generalize better.

## Lessons learned

* Should have aim for small incremental progress rather optimizing for future benefits. I could have spent an hour cleaning the image classes using the file browser compare to spending 15 hours drawing bounding boxes. Yes, I would probably have to repeat the labeling for future approaches; however, I found that the most benefit was leveraging the limited submission that is allowed per week. Having a reliable validation set is most important at the start.
  * If I had more time for this competition, the method I started with wouldn't be a waste since I learned a lot of the data I was working with and it allowed for more complex experiment.
* Due to the tremendous amount of time I spent to label the data, I wasn't able to make as much submission as I would have liked.
* The competition did not have a detail direction on labeling the data. There were many images in the training set that were extremely confusing so it seems like the winner of the competition could be likely in labeling in a way that is consistent with the data provider.

## Future Ideas

* Increase the number of attributes for the images which would help in selecting and augmenting the data. By having a richer attribute list, one can selectively target area that the model isn't performance well at like extra curvy symbols or removing the rare symbols. Please view [labeling-guide](labeling-guide.md) for examples of below.
  * noise
    * noise_type : does it contain side sticks, grid, vertical lines, horizontal, specks
    * noise_level : how noisy is the image percentage from 0 to 1.
    * we can leverage this by determine what type of noise exist in the data and how much so that we can select augmentation that matches this or we can remove the ones that are too noisy that could degrade the model performance.
  * angle : how much is the symbol slated
    * we can leverage this by determine what the range and which angles we lack. I doubt mirror reflect of the sybmol is a good idea since IV will turn to VI.
  * uniqueness : how uncommon is this font or shape of this symbol.
    * we can leverage this be determine if we need to upsample these rare symbol .
  * curviness : how straight or curvy the handwriting is.
    * this is relates to uniqueness but more specific to the line shape
  * dot_format : what is the dot shape
  * disjoined : distance between each symbol
  * line_thickness : how thick the lines are or how grainy the lines are.
  * incompleteness : what fraction of the symbol is complete
* Still I have position of the symbol
  * move the symbol around the page
  * resize just the symbol while adjusting the image size and aspect ratio

