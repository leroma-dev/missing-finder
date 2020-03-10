from flask import json

from libs.models import FaceBundle


class FrameModel:
    file_name: str
    frame_count: int
    face_list: list

    def __init__(self, filename: str, frame_count: int):
        self.file_name = filename
        self.frame_count = frame_count
        print('FrameModel Init -- {}@{}'.format(self.file_name, self.frame_count))

    def add_face(self, face: FaceBundle):
        self.face_list.append(face)

    def set_face_list(self, face_list: list):
        self.face_list = face_list

    def get_face_list(self) -> list:
        return self.face_list

    def get_file_name(self) -> str:
        return self.file_name

    def get_frame_count(self) -> int:
        return self.frame_count

    def get_face_count(self) -> int:
        return len(self.face_list)

    def to_data(self):
        json_face_list = []
        if len(self.get_face_list()) > 0:
            for i in range(0, len(self.get_face_list())):
                face = self.get_face_list()[i]
                json_face_list.append(face)
        else:
            print('No Faces @ {}'.format(self.frame_count))
        json_data = {
            "fileName": self.file_name,
            "frameCount": self.frame_count,
            "faceList": json_face_list
        }
        return json_data
