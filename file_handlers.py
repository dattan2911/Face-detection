import os
import fnmatch
import pickle
import faces_recognizer

# the dir KNOWN_FACES_DIRECTORY use to save/ find pkl file
KNOWN_FACES_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + "/KNOWN_FACES_DIRECTORY"

# create file in directory
def create_file (name) :
	try :
		os.mkdir(KNOWN_FACES_DIRECTORY)
	except FileExistsError:
		pass
# save encoding file into file pkl
def save_encodings (name) :
	with open(f"{KNOWN_FACES_DIRECTORY}/{name}"+".pkl", "wb") as file :
		pickle.dump(faces_recognizer.KNOWN_FACES_ENCODINGS, file)
# load infor from pkl file 
def load_encodings (name) :
	with open(f"{KNOWN_FACES_DIRECTORY}/{name}", "rb") as file :
		return pickle.load(file)
# load each pkl file into KNOWN_FACES list for recognization
def load_known_faces () :
	KNOWN_FACES = {}
	try:
		for _,_,files in os.walk(f"{KNOWN_FACES_DIRECTORY}") :
			for f in fnmatch.filter(files,'*.pkl'):
				KNOWN_FACES[os.path.basename(f).split('.')[0]] = load_encodings(os.path.basename(f))
	except :
		pass
	return KNOWN_FACES