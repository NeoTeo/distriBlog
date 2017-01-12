import sys
import argparse
import ntpath

# For calling shell scripts
from subprocess import call, Popen, PIPE

parser = argparse.ArgumentParser()
parser.add_argument('--text', nargs='?', type=argparse.FileType('r'), help='A text file.', default=sys.stdin)
parser.add_argument('--image', help='An image file.')
parser.add_argument('--video', help='An video file.')
parser.add_argument('--audio', help='An audio file.')
parser.add_argument('--author', help='The author of the post.')
parser.add_argument('--date', help='The date of the post. Defaults to current date.')
parser.add_argument('--time', help='The time of the post. Defaults to current time.')

args = parser.parse_args()

#print(args)
file_to_read = args.text
#print(file_to_read.name)

# for now we use magic numbers but will read from a config file 

#call(["ipfs", "id"])
# get the last post by resolving the ipns 
p = Popen(['ipfs', 'name', 'resolve', 'QmRzsihDMWML1dNPa51qwD2dacvZPfTrqsQt4pi1DWGJFP'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
#output = p.communicate(b"blabla")
for line in p.stdout.readlines():
    prev_post_hash = ntpath.basename(line.strip())

#print("prev_post is : ")
#print(prev_post)

#print(output[0])
#print(ntpath.basename(output[0]).strip())
#print(file_to_read.read())
print('<html>')
print('<body>')
print('<h1>')
print('first post<br>')
print('</body>')
print('<data-prev-post-hash=\"' + prev_post_hash.decode() + '\"/>')
print('</html>')

