import sys
import argparse
import ntpath

# For calling shell scripts
from subprocess import call, Popen, PIPE

import re # regular expressions

parser = argparse.ArgumentParser()
parser.add_argument('--text', nargs='?', type=argparse.FileType('r'), help='A text file.', default=sys.stdin)
parser.add_argument('--image', help='An image file.')
parser.add_argument('--video', help='An video file.')
parser.add_argument('--audio', help='An audio file.')
parser.add_argument('--title', help='The title of the post.')
parser.add_argument('--author', help='The author of the post.')
parser.add_argument('--date', help='The date of the post. Defaults to current date.')
parser.add_argument('--time', help='The time of the post. Defaults to current time.')
parser.add_argument('--outfile', help='The name of the output file. Defaults to post.html.')

args = parser.parse_args()

#print(args)
file_to_read = args.text
#print(file_to_read.name)

# for now we use magic numbers but will read from a config file 
ipns_hash = "QmRzsihDMWML1dNPa51qwD2dacvZPfTrqsQt4pi1DWGJFP"
#call(["ipfs", "id"])
# get the last post by resolving the ipns 
p = Popen(['ipfs', 'name', 'resolve', ipns_hash], stdin=PIPE, stdout=PIPE, stderr=PIPE)
for line in p.stdout.readlines():
    prev_post_hash = ntpath.basename(line.strip())

if args.outfile is not None:
    out_filename = args.outfile
else:
    out_filename = 'post.html'

# open a file to write to
outfile = open(out_filename, 'x')

#print("prev_post is : ")
#print(prev_post)

#print(ntpath.basename(output[0]).strip())
#print(file_to_read.read())
outfile.write('<html>')
outfile.write('<body>')
post_title = args.title
if post_title is not None:
    outfile.write('<h1>' + post_title + '</h1>')
if file_to_read is not None:
    post_text = file_to_read.read()
    outfile.write(post_text)

outfile.write('<br>')
outfile.write('<a href=\"https://ipfs.io/ipfs/' + prev_post_hash.decode() + '\">[Previous post]</a>')
outfile.write('</body>')
outfile.write('<data-prev-post-hash=\"' + prev_post_hash.decode() + '\"/>')
outfile.write('</html>')

outfile.close()

# Add the new post to the IPFS network
p = Popen(['ipfs', 'add', '-r', out_filename], stdin=PIPE, stdout=PIPE, stderr=PIPE)
# Compile regular expression to extract hash
regex = re.compile(b'^added (Qm[\w]{44})')
for line in p.stdout.readlines():
    matches = regex.search(line)
    post_hash = matches.group(1)
    print("adding resulted in", post_hash)

# Publish the post as the IPNS 
if post_hash:
    p = Popen(['ipfs', 'name', 'publish', post_hash], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    print("Published ",post_hash," to ipns ")
    for line in p.stdout.readlines():
        print("output is ",line)
