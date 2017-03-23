import sys
import argparse
import ntpath
import time
import io

# For calling shell scripts
from subprocess import call, Popen, PIPE

import re                   # regular expressions
import os.path              # for checking files exist

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--text_file', nargs='?', type=argparse.FileType('r'), help='Name of text file.', default=sys.stdin)
    parser.add_argument('--root_hash', help='The IPNS root hash.')
    parser.add_argument('--image_files', nargs='*', help='Names of image files.')
    parser.add_argument('--video_files', nargs='*', help='Name of video file.')
    parser.add_argument('--audio_files', nargs='*', help='Name of audio file.')
    parser.add_argument('--title', help='The title of the post.')
    parser.add_argument('--author', help='The author of the post.')
    parser.add_argument('--date', help='The date of the post. Defaults to current date.')
    parser.add_argument('--time', help='The time of the post. Defaults to current time.')
    parser.add_argument('--outfile', help='The name of the output file. Defaults to post.html.')

    args = parser.parse_args()

    return args

def write_post(post_data, root_post_hash, out_filename):
    # open a file to write to
    try:
        #outfile = open(out_filename, 'x')
        outfile = io.StringIO()
    except IOError as e:
        print("Could not create file", out_filename)
        print("Error:", e.strerror)
        sys.exit()

    outfile.write('<html>')
    outfile.write('<body>')

    post_time = post_data.get('post_time', None)
    post_date = post_data.get('post_date', None)

    outfile.write('<h2>' + post_date + " " + post_time + '</h2>')

    post_title = post_data.get('post_title', None)
    if post_title is not None:
        outfile.write('<h1>' + post_title + '</h1>')

    post_text = post_data.get('post_text', None)
    if post_text is not None:
        outfile.write(post_text)

    image_hashes = post_data.get('image_hashes', None)
    if image_hashes is not None:
        outfile.write('<p>')
        for hash in image_hashes:
            outfile.write('<img src=\"https://ipfs.io/ipfs/' + hash + '\">')
            outfile.write('<br>')
        outfile.write('</p>')

    audio_hashes = post_data.get('audio_hashes', None)
    if audio_hashes is not None:
        outfile.write('<p>')
        for hash in audio_hashes:
            outfile.write('<audio controls>')
            outfile.write('<source src=\"https://ipfs.io/ipfs/' + hash + '\">')
            outfile.write('<br>')
            outfile.write('</audio>')
        outfile.write('</p>')

    video_hashes = post_data.get('video_hashes', None)
    if video_hashes is not None:
        outfile.write('<p>')
        for hash in video_hashes:
            outfile.write('<video width=\"800\" height=\"600\" controls>')
            outfile.write('<source src=\"https://ipfs.io/ipfs/' + hash + '\">')
            outfile.write('<br>')
            outfile.write('</video>')
        outfile.write('</p>')

    if root_post_hash is not None:
        outfile.write('<p>')
        outfile.write('<data-prev-post-hash=\"' + root_post_hash + '\"/>')

        outfile.write('<a href=\"https://ipfs.io/ipfs/' + root_post_hash + '\">[Previous post]</a>')
        outfile.write('</p>')

    outfile.write('</body>')
    outfile.write('</html>')


    try:
        outfile2 = open(out_filename, 'x')
        outfile2.write(outfile.getvalue())
        outfile2.close()

    except IOError as e:
        print("Could not create file", out_filename)
        print("Error:", e.strerror)
        
    outfile.close()

def add_to_IPFS(filename):

    # Early out if file doesn't exist
    if os.path.exists(filename) is not True:
        return

    # Add the file to the IPFS network
    p = Popen(['ipfs', 'add', '-q', filename], stdin=PIPE, stdout=PIPE, stderr=PIPE)

    # Compile regular expression to extract hash
    for line in p.stdout.readlines():
        post_hash = line.strip().decode()
        print("adding resulted in", post_hash)

    return post_hash

def publish(post_hash):
    # Publish the post as the IPNS 
    if post_hash:
        p = Popen(['ipfs', 'name', 'publish', post_hash], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        print("Published ",post_hash," to ipns ")
        lines = p.stdout.readlines()
             
        for line in p.stdout.readlines():
            print("output is ",line)


def get_root_post_hash(root_ipns_hash):
    # get the last post by resolving the ipns 
    p = Popen(['ipfs', 'name', 'resolve', root_ipns_hash], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    prev_post_hash = None

    for line in p.stdout.readlines():
        prev_post_hash = ntpath.basename(line.strip())

    if prev_post_hash is not None:
        return prev_post_hash.decode()

    return

def load_defaults(defaults):
    print("defaults in: ", defaults)
    config_file = 'defaults.cfg'
    if os.path.exists(config_file) is not True:
        return

    with open(config_file) as file:
        # use regex to split into a key and a value
        regex = re.compile('(\w+)\s*=\s*(\w+)')
        for line in file.readlines():
            matches = regex.search(line)
            key = matches.group(1)
            value = matches.group(2)
            print("adding key", key, " and value ", value)
            if key is not None and value is not None:
                defaults[key] = value

def extract_post_data(args):

    post_data = {}

    # If the date for a post is not given, use today's date.
    post_date = args.date
    if post_date is None:
        post_date = time.strftime("%d/%m/%Y")

    post_data['post_date'] = post_date

    # If the time for a post is not given, use now.
    post_time = args.time
    if post_time is None:
        post_time = time.strftime("%X")

    post_data['post_time'] = post_time

    post_title = args.title
    if post_title is not None:
        post_data['post_title'] = post_title

    text_to_read = args.text_file

    # Post text is either from a file or stdin
    if text_to_read is not None:
        post_text = text_to_read.read()
    else:
        sys.exit('Error! Post text is missing.')

    post_data['post_text'] = post_text


    # get image files as hashes
    if args.image_files is not None:
        image_hashes = get_file_hashes(args.image_files)

        if len(image_hashes) is not 0:
            post_data['image_hashes'] = image_hashes

    # get sound files as hashes
    if args.audio_files is not None:
        audio_hashes = get_file_hashes(args.audio_files)

        if len(audio_hashes) is not 0:
            post_data['audio_hashes'] = audio_hashes

    # get video files as hashes
    if args.video_files is not None:
        video_hashes = get_file_hashes(args.video_files)

        if len(video_hashes) is not 0:
            post_data['video_hashes'] = video_hashes

    return post_data

def get_file_hashes(files):
    file_hashes = []
    for file in files:
        print("file found", file)
        file_hash = add_to_IPFS(file)
        if file_hash is not None:
            file_hashes.append(file_hash)

    return file_hashes

def main():
    defaults = {}

    # Python is pass by reference for mutable objects.
    load_defaults(defaults)

    args = parse_arguments()

    # if requested via args, store the args as defaults
    #store_defaults(defaults, args)
    
    if args.outfile is not None:
        out_filename = args.outfile
    else:
        out_filename = 'post' + time.strftime("%d%m%Y") + time.strftime("%H%M%S") + '.html'

    post_data = extract_post_data(args)

    print(post_data)

    root_post_hash = get_root_post_hash(defaults['root_hash'])

    write_post(post_data, root_post_hash, out_filename)

#def write_post(post_text, out_filename, root_post_hash, post_title):
    post_hash = add_to_IPFS(out_filename)

    publish(post_hash)

main()
