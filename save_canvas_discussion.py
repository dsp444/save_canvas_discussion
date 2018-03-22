#######################
# Script that will convert discussion posts from Canvas and save them to files.
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
#   1) Give it a course ID and discussion ID - the script will tell you the web address to use to get
#      your discussion posts.  Copy and paste this address into a browser and save the results as a file.
#   2) Once you have the posts saved as a file, run this script with a filename as the argument and it will
#      process the file and save the posts into individual HTML files.
# 
#
# Version 1.0    Dan Puperi    3/22/2018
# 
#
import sys,json,os

OUT=sys.stdout.write
CANVAS_URL = 'https://utexas.instructure.com/api/v1/courses/%s/discussion_topics/%s/view?include_new_entries=1&include_enrollment_state=1'
PYTHON_VER = 3

#######################
# Write each post to an individual html file.
# The format of the file is the same to the HTML files from downloaded text entry assingments on Canvas
# If file exists, append the new post to the end of the file.
#
def write_post_to_file( path, name, id, post, date, title="Discussion Posts" ):

#     Set the file name
    fname = path + '/' + name.strip().replace(' ','_').replace("'",'') + '_' + str(id) + '.html'
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
            file.write( '<div style="width: 600px; margin: 20px auto; border: 1px solid #888; padding: 20px;">\n' )
            file.write( date + '\n' )
            file.write( post.encode( 'utf8' ).decode( 'ascii', 'ignore' ) + '\n' )
            file.write( '</div>\n' )
            file.write( '</body>\n' )
            file.write( '</html>\n' )
    else:

#     Create a new file - simple HTML file with the discussion post.
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
            file.write( '<div style="width: 600px; margin: 20px auto; border: 1px solid #888; padding: 20px;">\n' )
            file.write( date + '\n' )
            file.write( post.encode( 'utf8' ).decode( 'ascii', 'ignore' ) + '\n' )
            file.write( '</div>\n' )
            file.write( '</body>\n' )
            file.write( '</html>\n' )
#
# End of write_post_to_file()
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
    print( os.path.dirname(fname) )
#     Open the file - different ways for Python 2 versus 3
    if PYTHON_VER == 3:
        with open( fname, 'r', encoding='utf8' ) as file:
            file_text = file.read()
    else:
        with open( fname ) as file:
            file_text = file.read().decode( 'utf8' )

#     If the file starts with a "while(1);", remove it from the text.    
    if file_text[0] == 'w':
    	text_to_convert = file_text.encode( 'utf8' ).decode( 'ascii', 'ignore' )[9:]
    else:
    	text_to_convert = file_text.encode( 'utf8' ).decode( 'ascii', 'ignore' )

#     Use the json module to read the text into JSON format
    data = json.loads( text_to_convert )

#     Loop through all participants and get name and ids of students
    for student in data['participants']:
        id = student['id']
        name = student['display_name']
    
#     Loop through all the discussion posts and match to the ones that this student posted.
#     If find a match, write it to a file.
        message = '' 
        for post in data['view']:
            if post['user_id'] == id:
                write_post_to_file( os.path.dirname( fname ), name, id, post['message'], post['updated_at'], os.path.basename( fname ).split('.')[0] )
#
# End of get_discussion_posts()
#######################


#######################
# The usage function just shows how to run the program
#
def usage():
    OUT( '\nCanvas discussion thread reader\n\n' )
    OUT( ' usage: get_canvas_discussion.py COURSE_ID DISCUSSION_ID\n' )
    OUT( '    or: get_canvas_discussion.py filename\n\n')
    OUT( '   The COURSE_ID and DISCUSSION_ID can be found on the URL for the Canvas discussion thread.\n' )
    OUT( '   For example: https://utexas.instructure.com/courses/1213320/discussion_topics/2926596\n' )
    OUT( '   The COURSE_ID is 122332 and the DISCUSSION_ID is 2926596.\n\n' )
    OUT( '   If the script is run with the COURSE_ID and DISCUSSION_ID, it will simply tell you the web address\n' )
    OUT( '   to use to download you discussion posts from Canvas.\n\n') 
    OUT( '   If the script is run with a filename, it will read the file and save posts for each student\n' )
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

# If there isn't 3 command line arguments (get_canvas_discussion.py COURSE_ID DISCUSSION_ID), then 
# display the instructions of how to use this program.
    if len(sys.argv) != 3 and len(sys.argv) != 2:
        usage()
        sys.exit(1)

# Collect input data from command line and pass that to the get_discussion_posts() function
    if len(sys.argv) == 3:
        course_id = sys.argv[1]
        discussion_id = sys.argv[2]
        OUT( '\nCopy and paste this URL into your browser to show all discussion posts into JSON format.\n ')
        OUT( 'Once you can see the JSON text in your browser, save it as a file on you computer to process\n ')
        OUT( 'using this program with the file name as the command line input.\n' )
        address = CANVAS_URL % ( course_id, discussion_id )
        OUT( '%s\n\n' % address )
    else:
        get_discussion_posts( sys.argv[1] )

    sys.exit(0)
