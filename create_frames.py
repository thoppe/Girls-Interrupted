'''
'''
import os, docopt, sys
args = {
    "--fps":1,
    "--qscale":1,
    "--f_movie":sys.argv[1],
    "--extension":".jpg",
}

f_movie = sys.argv[1]
assert(os.path.exists(f_movie))

name = os.path.basename(f_movie)

args["save_dest"] = os.path.join('data', 'frames', name)
os.system('mkdir -p "{save_dest}"'.format(**args))

first_frame = os.path.join(args['save_dest'], "000001.jpg")
if os.path.exists(first_frame):
    print "Skipping {}, first frame exists".format(f_movie)
    exit(0)


cmd = 'avconv -y -r {--fps} -an -q:v {--qscale} "{save_dest}/%06d{--extension}" -i "{--f_movie}"'
cmd = cmd.format(**args)
os.system(cmd)


