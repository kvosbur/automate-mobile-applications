# automate-mobile-applications

# GOTCHAS
- When cloning this repo please add the `--recurse-submodules` argument on.
- Note that lib is its own git repo so commits must be made explicitly in that folder

## Outside Setup

### Appium
`npm i --location=global appium`

### adb/android tooling

## Next Steps
- get android emulator setup with google play store
- download apks for necessary applications
- See if apks can be run on non google play store emulators
- open up an application and navigate to ad
- capture images on time interval from ad for a specified amount of time
- For each image, track the following information:
    - session (probably done by folder)
    - time into ad image was taken
    - ui automator screen contents at the time. (curious to know if it is only rendered or not)
    - number of ad actions take to get to this point
    - source game
- set repeat process to reopen app and get images for a new ad
- Filter out images at the end where there is no difference between them