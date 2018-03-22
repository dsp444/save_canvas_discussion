# save_canvas_discussion
Tool to convert JSON formatted discussion posts on Canvas LMS into HTML files - similar to saving student text-entry assignments. Canvas allows you to download all submissions to assignments, but there is no way to do the same thing with discussion posts.  However, the data is available in JSON format, it just needs parsed into readable files.  This script will parse the data and save it into individual HTML files for each student.  The format of the HTML files is the same as the format of the HTML files from downloaded assignment submissions.

Unfortunately, Canvas requires Bearer authentication to get access to the data, which is a pain to do through the API and you have to go through institutional access.  So this Python script cannot get the data directly from the Canvas website, you have to download it into a text file first.

 The script can be run 2 ways - with 2 different types of inputs:
   1) Give it a course ID and discussion ID - the script will tell you the web address to use to get your discussion posts.  Copy and paste this address into a browser and save the results as a file.
   2) Once you have the posts saved as a file, run this script with a filename as the argument and it will process the file and save the posts into individual HTML files.
