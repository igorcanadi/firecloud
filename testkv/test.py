
from subprocess import Popen, PIPE, STDOUT
p = Popen(['./runner'], stdin=PIPE, stdout=PIPE)
print 'Client Forked.'
out, err = p.communicate()
print ":" * 79
print out, err
print ":" * 79
