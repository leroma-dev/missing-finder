import numpy


class FaceBundle:
    filename = ''
    file_extension = ''
    face_id = ''
    location = []
    encodings = []
    landmarks = []
    is_known = False

    def __init__(self, filename, face_id):
        self.filename = filename
        self.face_id = face_id
        print('FaceBundle Init -- {}@{}'.format(self.face_id, self.filename))

    def setLocation(self, location):
        self.location = location

    def setEncodings(self, encodings):
        self.encodings = encodings

    def setLandmarks(self, landmarks):
        self.landmarks = landmarks

    def set_is_known(self, value):
        self.is_known = value

    def get_is_known(self):
        return  self.is_known

    def getLocation(self):
        return self.location

    def getEncodings(self):
        return self.encodings

    def getLandmarks(self):
        return self.landmarks

    def getName(self):
        return "{}@{}".format(self.face_id, self.filename)

    def toData(self):
        jsonData = {
            "faceId": self.face_id,
            "origin": self.filename,
            "isKnown": self.is_known,
            "locations": self.location, 
            "encoding": self.encodings.tolist(),
            "landmarks": self.landmarks
        }
        # result = json.dumps(jsonData)
        return jsonData

    def parseJson(self, json_data):
        face_bundle = FaceBundle(json_data['origin'], json_data['faceId'])
        face_bundle.setLocation(json_data['locations'])
        face_bundle.setEncodings(numpy.array(json_data['encoding']))
        face_bundle.setLandmarks(json_data['landmarks'])
        return face_bundle
