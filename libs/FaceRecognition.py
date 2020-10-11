from .models.FaceBundle import FaceBundle
from libs.S3Util import S3Util
from PIL import Image, ImageDraw
import glob, os, codecs, json
import face_recognition
import io
import tempfile

class FaceRecognition:
    def __init__(self, storageFolderPath='storage/',
        knownFolderPath='known/',
        unknownFolderPath='unknown/',
        outputFolderPath='output/',
        outputData='outputData.json',
        tolerance=0.6,
        s3_util=None):

        self.storageFolderPath = storageFolderPath
        self.knownFolderPath = knownFolderPath
        self.unknownFolderPath = unknownFolderPath
        self.outputFolderPath = outputFolderPath

        self.toleranceRate = tolerance
        self.knownFaces = []
        self.s3_util = s3_util

    #
    #   Generic
    #
    def set_known_folder_path(self, knownFolderPath):
        self.knownFolderPath = knownFolderPath

    def set_unknown_folder_path(self, unknownFolderPath):
        self.unknownFolderPath = unknownFolderPath

    def set_ouput_folder_path(self, outputFolderPath):
        self.outputFolderPath = outputFolderPath

    def set_ouput_data(self, outputData):
        self.outputData = outputData

    #
    #   Private Functions
    #

    #
    #   Dada uma imagem, Retorna uma lista com todas as Faces presentes
    #
    def __parse_faces(self, filePath, image_read) -> list:
        listFaces: list = []

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

    def __has_match(self, knownEncodings, faceBundle, tolerance, debug=True):
        matches = face_recognition.compare_faces(knownEncodings, faceBundle.getEncodings(),
                                                 tolerance=tolerance)
        if debug:
            for i in range(0, len(self.knownFaces)):
                if True == matches[i]:
                    print(faceBundle.getName(), '==', self.knownFaces[i].getName())
        return matches

    def __draw_image(self, drawInstance, faceBundle, label, drawBox=True, drawLandmarks=True, drawLabel=True):
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

    def add_known_face(self, source_file_path) -> FaceBundle:
        with tempfile.TemporaryFile() as data:
            self.s3_util.download_file(data, source_file_path)
            image_read = face_recognition.load_image_file(data)

        faceBundleList = self.__parse_faces(source_file_path, image_read)
        
        return faceBundleList[0]

    def add_known(self, face):
        if face:
            self.knownFaces.append(face)

    def find_matches(self, filePath, tolerance, image_read=None, draw_matches=True, id='') -> list:
        faceList: list = []

        # Download image from S3
        with tempfile.TemporaryFile() as data:
            self.s3_util.download_file(data, filePath)
            image_read = face_recognition.load_image_file(data)

        #   Find Faces
        faceBundleList = self.__parse_faces(filePath, image_read)

        #   Prepare to Draw
        if draw_matches:
            pil_image = Image.fromarray(image_read)
            draw = ImageDraw.Draw(pil_image)

        #   Prepare to Match
        knownFacesEncoding = []
        for knownFace in self.knownFaces:
            knownFacesEncoding.append(knownFace.getEncodings())

        for faceBundle in faceBundleList:
            matches = self.__has_match(knownFacesEncoding, faceBundle, tolerance)
            if draw_matches and len(matches) > 0 and True in matches:
                first_match_index = matches.index(True)
                name = self.knownFaces[first_match_index].getName()
                self.__draw_image(draw, faceBundle, name, drawBox=True)
                b = io.BytesIO()
                pil_image.save(b, 'jpeg')
                self.s3_util.upload_file(b.getvalue(), self.outputFolderPath+"result_"+id+".jpg")
                faceBundle.set_is_known(True)
            faceList.append(faceBundle.toData())
        return faceList

    def mark_face(self, face_id):
        file_list = glob.glob('result_{}_*.jpg'.format(face_id))
        file_count = 0
        for file in file_list:
            self.find_matches(file, id='{}_{}'.format(face_id, file_count))
            file_count += 1
        return file_count
