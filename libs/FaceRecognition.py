from PIL import Image, ImageDraw
import glob, os, codecs, json
import face_recognition

from .models.FaceBundle import FaceBundle


class FaceRecognition:
    def __init__(self, storageFolderPath='./storage/',
                 knownFolderPath='./known/',
                 unknownFolderPath='./unknown/',
                 outputFolderPath='./output',
                 outputData='outputData.json',
                 tolerance=0.6):

        self.storageFolderPath = storageFolderPath
        self.knownFolderPath = knownFolderPath
        self.unknownFolderPath = unknownFolderPath
        self.outputFolderPath = outputFolderPath

        # self.faceBundleFile = storageFolderPath+'facebundlefile.obj'
        self.csvFile = outputData
        self.toleranceRate = tolerance
        self.knownFaces = []


        # if os.path.exists(self.faceBundleFile):
        #     face_file = open(self.faceBundleFile, 'rb')
        #     self.knownFaces = pickle.load(face_file)
        #     face_file.close()
    #
    #   Generic
    #
    def setKnownFolderPath(self, knownFolderPath):
        self.knownFolderPath = knownFolderPath

    def setUnknownFolderPath(self, unknownFolderPath):
        self.unknownFolderPath = unknownFolderPath

    def setOuputFolderPath(self, outputFolderPath):
        self.outputFolderPath = outputFolderPath

    def setOuputData(self, outputData):
        self.outputData = outputData

    #
    #   Private Functions
    #

    #
    #   Dada uma imagem, Retorna uma lista com todas as Faces presentes
    #
    def __parseFaces(self, filePath, image_read=None) -> list:
        listFaces: list = []
        # Load test image to find faces in
        if image_read is None:
            image_read = face_recognition.load_image_file(filePath)

        # File Identification
        filename_w_ext = os.path.basename(filePath)
        filename, file_extension = os.path.splitext(filename_w_ext)

        # Find faces in test image
        # print ("image read:" + image_read)
        face_locations = face_recognition.face_locations(image_read)
        face_encodings = face_recognition.face_encodings(image_read, face_locations)
        face_landmarks = face_recognition.face_landmarks(image_read)

        count = 0
        for location, encodings, landmarks in zip(face_locations, face_encodings, face_landmarks):
            faceBundle = FaceBundle(filename, count)
            faceBundle.setLocation(location)
            faceBundle.setEncodings(encodings)
            faceBundle.setLandmarks(landmarks)
            listFaces.append(faceBundle)
            count += 1
        return listFaces

    def __hasMatch(self, knownEncodings, faceBundle, tolerance, debug=True):
        matches = face_recognition.compare_faces(knownEncodings, faceBundle.getEncodings(),
                                                 tolerance=tolerance)
        if debug:
            for i in range(0, len(self.knownFaces)):
                if True == matches[i]:
                    print(faceBundle.getName(), '==', self.knownFaces[i].getName())
        return matches

    def __drawImage(self, drawInstance, faceBundle, label, drawBox=True, drawLandmarks=True, drawLabel=True):
        top, right, bottom, left = faceBundle.getLocation()

        # Draw box
        if drawBox:
            drawInstance.rectangle(((left, top), (right, bottom)), outline=(255, 255, 0))

        # Draw Landmarks
        if drawLandmarks:
            for __, value in faceBundle.getLandmarks().items():
                drawInstance.line(value, fill=(27, 189, 230), width=1)

        # Draw label
        if drawLabel:
            text_width, text_height = drawInstance.textsize(label)
            drawInstance.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(255, 255, 0),
                                   outline=(255, 255, 0))
            drawInstance.text((left + 6, bottom - text_height - 5), label, fill=(0, 0, 0))

    #
    #   Public Functions
    #

    #
    #   Recorta todas as Faces de uma Imagem e as Salva
    #
    def pullFaces(self, imagePath, outputExtension='jpg'):
        listFaces = self.__parseFaces(imagePath)
        image = face_recognition.load_image_file(imagePath)
        for face in listFaces:
            top, right, bottom, left = face.getLocation()
            face_image = image[top:bottom, left:right]
            pil_image = Image.fromarray(face_image)
            resultPath = "{}/{}.jpg".format(self.outputFolderPath, face.getName())
            pil_image.save(resultPath)
        print("pullFaces -- {} Faces Found".format(len(listFaces)))
        print("pullFaces -- Done")

        return listFaces

    #
    # Known Faces
    #
    # def parseKnownFaces(self, image_extension = ''):
    #     if not self.knownFaces:
    #         files_regex = self.knownFolderPath + '*' + image_extension
    #         files = glob.glob(files_regex)
    #         for filename in files:
    #             faceBundleList = self.__parseFaces(filename)
    #             if len(faceBundleList) != 0:
    #                 self.knownFaces.append(faceBundleList[0])
    #             else:
    #                 print("Encoding Error on", filename)
    #         self.saveKnownFaces()

    def addKnownFace(self, filePath) -> FaceBundle:
        faceBundleList = self.__parseFaces(filePath)
        if len(faceBundleList):
            self.knownFaces.append(faceBundleList[0])
#            self.saveKnownFaces()
        return faceBundleList[0]

    def add_known(self, face):
        if face:
            self.knownFaces.append(face)

    def findMatches(self, filePath, tolerance, image_read=None, draw_matches=True, id='') -> list:
        faceList: list = []

        #   Find Faces
        faceBundleList = self.__parseFaces(filePath, image_read)

        #   Prepare to Draw
        if draw_matches:
            if image_read is None:
                image_read = face_recognition.load_image_file(filePath)
            pil_image = Image.fromarray(image_read)
            draw = ImageDraw.Draw(pil_image)

        #   Prepare to Match
        knownFacesEncoding = []
        for knownFace in self.knownFaces:
            knownFacesEncoding.append(knownFace.getEncodings())

        for faceBundle in faceBundleList:
            matches = self.__hasMatch(knownFacesEncoding, faceBundle, tolerance)
            if draw_matches and len(matches) > 0 and True in matches:
                first_match_index = matches.index(True)
                name = self.knownFaces[first_match_index].getName()
                self.__drawImage(draw, faceBundle, name, drawBox=True)
                pil_image.save('{}/result_{}.jpg'.format(self.outputFolderPath, id))
                faceBundle.set_is_known(True)
            faceList.append(faceBundle.toData())
        return faceList

    def parseFromJson(self, json_path):
        obj_text = codecs.open(json_path, 'r', encoding='utf-8').read()
        b_new = json.loads(obj_text)
        print()
        # a_new = np.array(b_new)
    # def __writeData(self, data):
    #     with open(self.csvFile, 'a') as csvFile:
    #         writer = csv.writer(csvFile)
    #         writer.writerow(data)
    #     csvFile.close()

    def mark_face(self, face_id):
        file_list = glob.glob('{}/result_{}_*.jpg'.format(self.outputFolderPath, face_id))
        file_count = 0
        for file in file_list:
            self.findMatches(file, id='{}_{}'.format(face_id, file_count))
            file_count += 1
        return file_count
