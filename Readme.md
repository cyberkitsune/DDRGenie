# DDR Genie
This repo contains a python module called "DDRGenie"

It is used to parse data out of the e-amusement screenshots taken from the *DanceDanceRevolution A* and *DanceDanceRevolutionn A20* arcade games.

## Requirements
* Python 3
* [tesseract-ocr](https://github.com/tesseract-ocr/tesseract) with both english and japanese training data
  * Slower / More accurate data recommended
* (Optional) A DeepAI key to enable 2x upscaling via [waifu2x](https://github.com/nagadomi/waifu2x)

## Installation
1. `pip install -R Requirements.txt`
2. (Optional) Write out your DeepAI key to `deepai_key.txt` in the working directory

## Usage
`python Genie.py [path_to_screenshot] [upscale] [debug]`

## Process
WIP

## Licence
MIT? MIT.