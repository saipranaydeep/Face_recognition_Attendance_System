# Automated attendance system using Face Recognition
This is an attendance system which automatically marks attendance on uploading group photo of the class.

## How to get this website on your device?

- Clone this repo using
  `git clone https://github.com/tekksick/attendance-system-using-faceRecognition`

- Go into the root of this directory.
  `cd attendance-system-using-faceRecognition`

- Now install the required dependencies.
  `pip install -r requirements.txt`

- To install dlib make sure python's version is 3.12.0 and you have visual studio for c++ on your device.
  
-  Then download this dlib file. `https://drive.google.com/file/d/11dkOCYUd72wikVIXRGiUclvKB3FHbiHY/view?usp=sharing`

- To run the game, run the following command,
  `python manage.py runserver`

- Open a web browser and navigate to `http://localhost:5000` to access the administration interface.

### How to use?

- Register students or professors by providing their name, EmailId, password uploading a picture of their face.
 
- Start taking attendance by selecting the batch details and uploading the group photos. The system will use the webcam to recognize faces and record attendance.

- View and export attendance records by clicking "download csv file" button.

## For developers

- This website uses a face_recognition (a module of python) based model.
- Other models like YOLO can also be used by changing this file.
- Make sure to add the dependencies in the requirements.txt file.
