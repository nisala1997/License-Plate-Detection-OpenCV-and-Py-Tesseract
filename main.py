import cv2
import imutils   # to resize our images
import pytesseract
import winsound  # Produce sound

pytesseract.pytesseract.tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # installing tesseract ocr directory

#Capturing number plate of vehicle.use quality camera more accurate
vid=cv2.VideoCapture(0)
while(True):
    ret,image=vid.read()
    cv2.imshow('image',image)
    if cv2.waitKey(1) & 0xFF == ord('q'):     # press 'q' to capturing photo
        break
    cv2.imwrite('CarPictures/car.jpg',image)  #it is save in this location
vid.release()
cv2.destroyAllWindows()

#now to read image file
image=cv2.imread('CarPictures/car.jpg')
#we will resize and standardise our image to 500
image=imutils.resize(image,width=500)
#we will display original image when it will start finding
cv2.imshow("Original Image",image) # here original image is the name of window can give your suitable name
#cv2.waitKey(0)

#now we will convert image to gray scale
#why we do is because it will reduce the dimension , also reduces complexity of image
#and yeah there are few algorithms like canny , etc which only works on grayscale images
gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
cv2.imshow("Gray Scale Image",gray)
#cv2.waitKey(0)

#now we will reduce noise from our image and make it smooth
gray=cv2.bilateralFilter(gray,11,17,17)
cv2.imshow("Smoother Image",gray)
#cv2.waitKey(0)

#now we will find the edges of images
edged=cv2.Canny(gray,170,200)
cv2.imshow("Canny edge",edged)
#cv2.waitKey(0)

#now we will find the contours based on the images.
cnts,new=cv2.findContours(edged.copy(),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
#so here cnts is contours which means that it is like the curve joining all the contiour points
#new is heirarchy-relationship
#RETR_LIST - it retrives all the contours but doesn't create any parent-child relationship
#CHAIN_APPROX_SIMPLE - it removes all the redundant points and compress the contour by saving memory

#we will create a copy of our original image to draw all the contours
image1=image.copy()
cv2.drawContours(image1,cnts,-1,(0,255,0),3)
cv2.imshow("Canny After Contouring",image1)
#cv2.waitKey(0)

#now we don't want all the contours we are intrested only in number plate
#but can't directly locate that so we will sort them on the basic of their areas
#we will select those area which are maximum so we will select top 30 areas
#but it will give sorted list as in order of min to maximum
#so for that we will reverse the order of sorting

cnts=sorted(cnts,key=cv2.contourArea,reverse=True)[:30]
NumberPlateCount=None

#to drow top 30 contours we will make copy of original image and use
image2=image.copy()
cv2.drawContours(image2,cnts,-1,(0,255,0),3)
cv2.imshow("Top 30 Contours",image2)
#cv2.waitKey(0)

#now we will run a for loop on our contours to find the best possible contour of our expectes number plate
count=0
name=1  #name of our cropped image

for i in cnts:
    perimeter=cv2.arcLength(i,True)
    #perimeter is also called as arcLength and we can find directly in python using arcLength function
    approx=cv2.approxPolyDP(i,0.02*perimeter,True)
    #approxPolyDP we have used because it approximates the curve of polygon with the precision
    if(len(approx)==4):  # 4 means it has 4 corner which well be most probably our number plate as it also has 4 corners
        NumberPlateCount=approx
        #now we will crop that rectangle part
        x , y , w , h =cv2.boundingRect(i)
        crp_img=image[y:y+h,x:x+w]
        cv2.imwrite(str(name)+'.png',crp_img)
        name+=1

        break

#now we will draw contour in our main image that we have identified as a number plate
cv2.drawContours(image,[NumberPlateCount],-1,(0,255,0),3)
cv2.imshow("Final Image",image)
#cv2.waitKey(0)

#we will crop only the part of number plate
crop_img_loc='1.png'
cv2.imshow("Cropped Image",cv2.imread(crop_img_loc))
#cv2.waitKey(0)

#now what we do is by using pytesseract module we will convert our image into text
text=pytesseract.image_to_string(crop_img_loc,lang='eng')
print("Number is : ",text)
text = ''.join(e for e in text if e.isalnum())  #modify our text no spaces

#create function read our database
def check_if_string_in_file(file_name, string_to_search):
    with open(file_name, 'r') as read_obj:
        for line in read_obj:
            if string_to_search in line:
                return True
    return False

#Produce beep sound for registered vehicle captured by camera and print
frequency = 2500
duration = 1200
if check_if_string_in_file('./Database/Database.txt', text) and text != "":
    print('Registered')
    winsound.Beep(frequency, duration)
else:
    print("Not Registered")
cv2.waitKey(0)
