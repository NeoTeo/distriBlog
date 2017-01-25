import sys
import argparse
import ntpath

# For calling shell scripts
from subprocess import call, Popen, PIPE

import re                   # regular expressions
import os.path              # for checking files exist

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--text_file', nargs='?', type=argparse.FileType('r'), help='Name of text file.', default=sys.stdin)
    parser.add_argument('--root_hash', help='The IPNS root hash.')
    parser.add_argument('--image_files', nargs='*', help='Names of image files.')
    parser.add_argument('--video_files', nargs='*', type=argparse.FileType('r'), help='Name of video file.')
    parser.add_argument('--audio_files', nargs='*', type=argparse.FileType('r'), help='Name of audio file.')
    parser.add_argument('--title', help='The title of the post.')
    parser.add_argument('--author', help='The author of the post.')
    parser.add_argument('--date', help='The date of the post. Defaults to current date.')
    parser.add_argument('--time', help='The time of the post. Defaults to current time.')
    parser.add_argument('--outfile', help='The name of the output file. Defaults to post.html.')

    args = parser.parse_args()

    return args

def write_post(post_data, root_post_hash, out_filename):
    # open a file to write to
    outfile = open(out_filename, 'x')

    outfile.write('<html>')
    outfile.write('<body>')

    post_title = post_data.get('post_title', None)
    if post_title is not None:
        outfile.write('<h1>' + post_title + '</h1>')

    post_text = post_data.get('post_text', None)
    if post_text is not None:
        outfile.write(post_text)

    outfile.write('<br>')
    outfile.write('<a href=\"https://ipfs.io/ipfs/' + root_post_hash + '\">[Previous post]</a>')

    image_hashes = post_data.get('image_hashes', None)
    for hash in image_hashes:
        outfile.write('<img src=\"https://ipfs.io/ipfs/' + hash + '\"><br>')

    outfile.write('</body>')
    outfile.write('<data-prev-post-hash=\"' + root_post_hash + '\"/>')
    outfile.write('</html>')

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
    for line in p.stdout.readlines():
        prev_post_hash = ntpath.basename(line.strip())

    return prev_post_hash.decode()

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
    image_hashes = get_image_hashes(args.image_files)

    if len(image_hashes) is not 0:
        post_data['image_hashes'] = image_hashes

    return post_data

def get_image_hashes(images):
    image_hashes = []
    for image in images:
        print("image found", image)
        image_hash = add_to_IPFS(image)
        if image_hash is not None:
            image_hashes.append(image_hash)

    return image_hashes

def main():
    defaults = {}

    # Python is pass by reference for mutable objects.
    load_defaults(defaults)

    args = parse_arguments()

    # if requested via args, store the args as defaults
    #store_defaults(defaults, args)
    

    root_post_hash = get_root_post_hash(defaults['root_hash'])

    if args.outfile is not None:
        out_filename = args.outfile
    else:
        out_filename = 'post.html'

    post_data = extract_post_data(args)

    print(post_data)

    write_post(post_data, root_post_hash, out_filename)

#def write_post(post_text, out_filename, root_post_hash, post_title):
    post_hash = add_to_IPFS(out_filename)

    publish(post_hash)

main()
