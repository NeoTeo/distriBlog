import sys
import argparse
import ntpath

# For calling shell scripts
from subprocess import call, Popen, PIPE

import re                   # regular expressions
import os.path              # for checking files exist

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--text_file', nargs='?', type=argparse.FileType('r'), help='Name of file containing post text.', default=sys.stdin)
    parser.add_argument('--root_hash', help='The IPNS root hash.')
    parser.add_argument('--image', help='An image file.')
    parser.add_argument('--video', help='An video file.')
    parser.add_argument('--audio', help='An audio file.')
    parser.add_argument('--title', help='The title of the post.')
    parser.add_argument('--author', help='The author of the post.')
    parser.add_argument('--date', help='The date of the post. Defaults to current date.')
    parser.add_argument('--time', help='The time of the post. Defaults to current time.')
    parser.add_argument('--outfile', help='The name of the output file. Defaults to post.html.')

    args = parser.parse_args()

    return args

def write_post(post_text, out_filename, root_post_hash, post_title):
    # open a file to write to
    outfile = open(out_filename, 'x')

    outfile.write('<html>')
    outfile.write('<body>')
    if post_title is not None:
        outfile.write('<h1>' + post_title + '</h1>')
    #if file_to_read is not None:
        #post_text = file_to_read.read()
    outfile.write(post_text)

    outfile.write('<br>')
    outfile.write('<a href=\"https://ipfs.io/ipfs/' + root_post_hash.decode() + '\">[Previous post]</a>')
    outfile.write('</body>')
    outfile.write('<data-prev-post-hash=\"' + root_post_hash.decode() + '\"/>')
    outfile.write('</html>')

    outfile.close()

def add_to_IPFS(out_filename):
    # Add the new post to the IPFS network
    p = Popen(['ipfs', 'add', '-r', out_filename], stdin=PIPE, stdout=PIPE, stderr=PIPE)

    # Compile regular expression to extract hash
    regex = re.compile(b'^added (Qm[\w]{44})')
    for line in p.stdout.readlines():
        matches = regex.search(line)
        post_hash = matches.group(1)
        print("adding resulted in", post_hash)

    return post_hash

def publish(post_hash):
    # Publish the post as the IPNS 
    if post_hash:
        p = Popen(['ipfs', 'name', 'publish', post_hash], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        print("Published ",post_hash," to ipns ")
        for line in p.stdout.readlines():
            print("output is ",line)


def get_root_post_hash(root_ipns_hash):
    # get the last post by resolving the ipns 
    p = Popen(['ipfs', 'name', 'resolve', root_ipns_hash], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    for line in p.stdout.readlines():
        prev_post_hash = ntpath.basename(line.strip())

    return prev_post_hash

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


def main():
    defaults = {}

    # Python is pass by reference for mutable objects.
    load_defaults(defaults)

    args = parse_arguments()

    # if requested via args, store the args as defaults
    #store_defaults(defaults, args)
    
    file_to_read = args.text_file

    # Here we need to ensure the text is either from a file or input directly as a string arg.
    if file_to_read is not None:
        post_text = file_to_read.read()
    else:
        sys.exit('Error! Post text is missing.')

    root_post_hash = get_root_post_hash(defaults['root_hash'])

    if args.outfile is not None:
        out_filename = args.outfile
    else:
        out_filename = 'post.html'

    write_post(post_text, out_filename, root_post_hash, args.title)

    post_hash = add_to_IPFS(out_filename)

    publish(post_hash)

main()
