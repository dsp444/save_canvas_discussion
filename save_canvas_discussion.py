#######################
# Script that will convert discussion posts from Canvas LMS and save them to files.
# Canvas allows you to download all submissions to assignments, but there is no way
# to do the same thing with discussion posts.  However, the data is available in JSON format,
# it just needs parsed into readable files.  This script will parse the data and save it into
# individual HTML files for each student.  The format of the HTML files is the same as the 
# format of the HTML files from downloaded assignment submissions.
#
# Unfortunately, Canvas requires Bearer authentication to get access to the data, which is 
# a pain to do through the API and you have to go through institutional access.  So this Python script 
# cannot get the data directly from the Canvas website, you have to download it into a text file first.
#
# The script can be run 2 ways - with 2 different types of inputs:
#   1) Give it 3 arguments: an institution name, course ID, and discussion ID.  If the script detects these inputs,
#      it will report the web address to use to get your discussion posts. Copy and paste this address into 
#      a browser and save the results as a file.
#   2) Once you have the posts saved as a file, run this script with a filename as the argument and it will
#      process the file and save the posts into individual HTML files.
# 
#
# Version 1.0    Dan Puperi    5/11/2018
# Version 1.01   Dan Puperi    11/1/2018 
#    - fixed file write error (because it tried to write to root dir) when path of input .json file
#      wasn't provided by the user
# Version 1.1    Seth Wilson   12/14/2018
#    - recursively reads through the 'replies' field of each post and adds them to the HTML output.
# Version 1.11   Dan Puperi    12/17/2018
#    - update to recording replies. Made it optional by setting a flag (default = True).  Reduced
#      arguments to write_replies_to_html function. Also created a global WIDTH variable.
# Version 1.12   Dan Puperi    01/03/2019
#    - fix error with replies to replies (not passing correct argument to recall of function)
# 
#
import sys,json,os

OUT=sys.stdout.write

# URL of Canvas API to download JSON formatted discussions
CANVAS_URL = 'https://%s.instructure.com/api/v1/courses/%s/discussion_topics/%s/view?include_new_entries=1&include_enrollment_state=1'

# Default is Python 3 until this script detects otherwise
PYTHON_VER = 3

# Set to true in order to recursively write replies to the HTML files
# It may be helpful to set this to False if checking for plagiarism
INCLUDE_REPLIES = True

# Set the width of the discussion post boxes
WIDTH = 600

#######################
# Write each post to an individual html file.
# The format of the file is the same to the HTML files from downloaded text entry assingments on Canvas
# If file exists, append the new post to the end of the file.
#
def write_post_to_file( path, name, id, post, date, id_to_name, title="Discussion Posts", replies={} ):
    if path == '': path = '.'

#     Set the file name
    fname = path + '/' + name.strip().replace(' ','_').replace("'",'') + '_' + str(id) + '.html'

#     If file already exists, append a new box with second discussion post
    if os.path.exists( fname ):
        with open( fname, 'r') as file:

#     First need to remove the </body> and </html> last line of the original file
#     There should be more elegant way to do this rather than reading all the lines, deleting the file,
#     and rewriting all except the last 2, but they are small files so it doesn't matter too much.
            lines = file.readlines()
        os.remove( fname )
        with open( fname, 'w' ) as file:
            for line in lines[0:-2]:
                file.write( line )

#     Now write a line break and the new post in its own div box
            file.write( '<br>\n')
            file.write( '<div style="width: %spx; margin: 20px auto; border: 1px solid #888; padding: 20px;">\n' % WIDTH )
            file.write( date + '\n' )
            file.write( post.encode( 'utf8' ).decode( 'ascii', 'ignore' ) + '\n' )
    else:

#     If file does not exist, create a new file - simple HTML file with the discussion post.
        with open( fname, 'w' ) as file:
            file.write( '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\n' )
            file.write( '          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n' )
            file.write( '<html xmlns="http://www.w3.org/1999/xhtml">\n' )
            file.write( '<head>\n' )
            file.write( '<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />\n' )
            file.write( '<title>%s: %s</title>\n' % (title,name) )
            file.write( '</head>\n' )
            file.write( '<body>\n' )
            file.write( '<h1>%s: %s</h1>\n' % (title,name) )
            file.write( '<div style="width: %spx; margin: 20px auto; border: 1px solid #888; padding: 20px;">\n' % WIDTH )
            file.write( date + '\n' )
            file.write( post.encode( 'utf8' ).decode( 'ascii', 'ignore' ) + '\n' )

#   if the post has replies, write those to the file as well.
    if replies and INCLUDE_REPLIES:
        write_replies_to_file( fname, id, replies, id_to_name, WIDTH )

#   finally, close the <div>, <body>, and <html> tags
    with open( fname, 'a+' ) as file:
        file.write( '</div>\n' )
        file.write( '</body>\n' )
        file.write( '</html>\n' )
#
# End of write_post_to_file()
#######################

#######################
# include replies to a post along with that post.
# called either from write_post_to_file or recursively.
def write_replies_to_file( fname, id, replies, id_to_name, width ):
    
#   decrement the width by 40 pixels to thread comments
    width = width - 40

#   loop through each reply
    for reply in replies:

#       ignore deleted reply:
        if not 'deleted' in reply:
        
#           write the reply to the file.
            with open( fname, 'a+') as file:
                file.write( '<br>\n')
                file.write( '<div style="width: %spx; margin: 5px auto; border: 1px solid #888; padding: 20px;">\n' % width )
                file.write( '<strong>' + id_to_name[reply['user_id']] + '</strong>\n' )
                file.write( reply['updated_at'] + '\n' )
                file.write( reply['message'].encode( 'utf8' ).decode( 'ascii', 'ignore' ) + '\n' )

#           if there are threaded replies, recursively write those as well.
            if 'replies' in reply.keys():
                write_replies_to_file( fname, id, reply['replies'], id_to_name, width )

#           close the reply's <div>
            with open( fname, 'a+') as file:
                file.write( '</div>\n')
#
# End of write_replies_to_file
#######################

#######################
# Get the discussion posts from the Canvas API website
# https://utexas.instructure.com/api/v1/courses/COURSE_ID/discussion_topics/DISCUSSION_ID/view?include_new_entries=1&include_enrollment_state=1
#
# Need to remove a "while(1);" from the beginning of the page, but after that it is just data in JSON format
# Use Python JSON reader to load the data into a dictionary and parse the data out.
# Call write_post_to_file function to actually create the files from the JSON data.
#
def get_discussion_posts( fname ):
#   Open the file - different ways for Python 2 versus 3
    if PYTHON_VER == 3:
        with open( fname, 'r', encoding='utf8' ) as file:
            file_text = file.read()
    else:
        with open( fname ) as file:
            file_text = file.read().decode( 'utf8' )

#   If the file starts with a "while(1);", remove it from the text.    
    if file_text[0] == 'w':
        text_to_convert = file_text.encode( 'utf8' ).decode( 'ascii', 'ignore' )[9:]
    else:
        text_to_convert = file_text.encode( 'utf8' ).decode( 'ascii', 'ignore' )

#   Use the json module to read the text into JSON format
    data = json.loads( text_to_convert )

#   create a dictionary that maps IDs to names; needed for replies.
    id_to_name = {}
    for student in data['participants']:
        id_to_name[student['id']] = student['display_name']

#   Loop through all participants and get name and ids of students
    for student in data['participants']:
        id = student['id']
        name = student['display_name']
    
#     Loop through all the discussion posts and match to the ones that this student posted.
#     If find a match, write it to a file.
        message = '' 
        for post in data['view']:
            if 'user_id' in post.keys():
                replies = {}
                if 'replies' in post.keys():
                    replies = post['replies']
                if post['user_id'] == id:
                    write_post_to_file( os.path.dirname( fname ), name, id, post['message'], post['updated_at'], id_to_name, os.path.basename( fname ).split('.')[0], replies )
#
# End of get_discussion_posts()
#######################


#######################
# The usage function just shows how to run the program
#
def usage():
    OUT( '\nCanvas discussion thread saver\n\n' )
    OUT( ' usage: save_canvas_discussion.py INSTITUTION COURSE_ID DISCUSSION_ID\n' )
    OUT( '    or: save_canvas_discussion.py FILENAME\n\n')
    OUT( '   The COURSE_ID and DISCUSSION_ID can be found on the URL for the Canvas discussion thread.\n' )
    OUT( '   For example: https://utexas.instructure.com/courses/1213320/discussion_topics/2926596\n' )
    OUT( '   The COURSE_ID is 122332 and the DISCUSSION_ID is 2926596 and you would run the script with the command:\n' )
    OUT( '   > save_canvas_discussion.py utexas 122332 2926596\n\n')        
    OUT( '   If the script is run as above, it will simply return the web address to use to display the discussion\n' )
    OUT( '   posts in JSON formatted file from Canvas.  Save this on your computer as a file for the next step.\n\n') 
    OUT( '   If the script is run with the filename that you saved from the previous step, it will save posts for each student\n' )
    OUT( '   in the current directory as an html file. Each students posts will be saved as a different html file\n' )
    OUT( '   and multiple posts from the same student will appear in a single html file for that student.\n\n' )
#
# End of usage()
#######################


#######################
# Entry point into the program
if __name__ == '__main__':

    if sys.version_info[0] < 3:
        PYTHON_VER = 2

# If there isn't 4 command line arguments (get_canvas_discussion.py INSTITUTION COURSE_ID DISCUSSION_ID), then 
# display the instructions of how to use this program.
    if len(sys.argv) != 4 and len(sys.argv) != 2:
        usage()
        sys.exit(1)

# Collect input data from command line and pass that to the get_discussion_posts() function
    if len(sys.argv) == 4:
        institute = sys.argv[1]
        course_id = sys.argv[2]
        discussion_id = sys.argv[3]
        OUT( '\nCopy and paste this URL into your browser to show all discussion posts into JSON format.\n ')
        OUT( 'Once you can see the JSON text in your browser, save it as a file on you computer to process\n ')
        OUT( 'using this program with the file name as the command line input.\n' )
        address = CANVAS_URL % ( institute, course_id, discussion_id )
        OUT( '%s\n\n' % address )
    else:
        get_discussion_posts( sys.argv[1] )

    sys.exit(0)
