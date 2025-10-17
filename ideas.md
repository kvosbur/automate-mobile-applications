# File structure

- Sessions (folder)
    - session (uuidv7 folder)
        - image_number_in_sequence.png
        - image_number_in_sequence.json

- Dataset
    - high_level_label_name (folder)
        - image_number_in_sequence.png
        - image_number_in_sequence.json

## Metadata Contents
- how long into ad the image was taken (i.e. what number of image is it into the ad)
- screen contents from appium at the time
- how many actions have been taken on the ad to get to this point
- source game application identifier
- detected labels (after initial learning hump and I want more training data. can be done async after the fact)
    - Note that in Dataset this has been corrected if initially made from model guess

## Lifecycle and maintaince

- NEVER actually delete session data. Any filtering of what images I would like to take should not affect initial session folder.
- Session folder is local only. Don't want to make Github angry.

# Misc Ideas

- Filter out what images to consider for training data by looking at difference between frames to get which ones are more meaningful.
    - Could be something like % different pixel colors, or some other faster to compute metric
- Parameterize appium configurations to make it easier to swap between different games
- Make label names hyper specific in the form of `<generic_label_name>-<further_clafier_such_as_color>`
    - This means that I can try training the model on more labels that are hyperspecific and less which are more generic. Should enable some intersting learning thoughts on what this does to accuracy after training
- Would like object detection to run within 2 seconds. Whether that means I need a smaller model or to run on my gaming computer for the gpu will be something I have to figure out. All training will likely happen on my computer.

# Goals
- Model should be able to run in less than 2 seconds on the MacBook
- Able to successfully traverse 90% of ads, and be able to dismiss the others on failure

# Helpful Links
- model preprocessing/training: https://docs.ultralytics.com/guides/model-training-tips/