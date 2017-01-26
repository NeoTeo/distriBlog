# A tiny script for making an append only blog that lives on the IPFS network.

The given root_hash will determine which blog the post will be pushed onto. 
If none is given the script will look for it in a defaults.cfg file.
The config file format is, one per line: 
    key = value 

## Usage:

    usage: post.py [-h] [--text_file [TEXT_FILE]] [--root_hash ROOT_HASH]
                [--image_files [IMAGE_FILES [IMAGE_FILES ...]]]
                [--video_files [VIDEO_FILES [VIDEO_FILES ...]]]
                [--audio_files [AUDIO_FILES [AUDIO_FILES ...]]] [--title TITLE]
                [--author AUTHOR] [--date DATE] [--time TIME]
                [--outfile OUTFILE]

## Examples

    echo 'This is the post text written inline.' | python post.py --title 'Title text' --image_files pic.png pic2.png --outfile newpost.html

## Todo
* If no outfile is given, output to a temp file that is deleted locally after being added to IPFS.
* Implement default date and time to be the time of posting.
* Implement video and audio files.
* Design post layout.
