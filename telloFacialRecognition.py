import sys
import traceback
import tellopy
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
import numpy
import time
import unixCharRead
import threading
import dlib

DISTANCE = 25
def flightControl(drone):
	global DISTANCE
	msg = unixCharRead.readChar()
	while True:
		if msg == "i":
			drone.forward(DISTANCE)
		elif msg == "k":
			drone.backward(DISTANCE)
		elif msg == "j":
			drone.left(DISTANCE)
		elif msg == "l":
			drone.right(DISTANCE)
		elif msg == "w":
			drone.up(DISTANCE)
		elif msg == "s":
			drone.down(DISTANCE)
		elif msg == "a":
			drone.clockwise(1)
		elif msg == "d":
			drone.counter_clockwise(1)
		elif msg == "t":
			drone.takeoff()
		elif msg == "y":
			drone.land()
			break
		elif msg == "q":
			drone.quit()
			break
		msg = unixCharRead.readChar()

def facialRecognition(drone):
	faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
	rectangleColor = (0,165,255)
	try:
		drone.connect()
		drone.wait_for_connection(60.0)

		container = av.open(drone.get_video_stream())

		tracker = dlib.correlation_tracker()
		
		trackingFace = False

		frameSkip = 300 #to eliminate initial lag
		while True:
			for frame in container.decode(video=0):
				
				if 0 < frameSkip:
                    			frameSkip = frameSkip - 1
                    			continue

				image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
				
				frame = numpy.array(frame.to_image()) #convert frame 
				facialFrame = frame #make a copy of frame 
				
				if not trackingFace:
					grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
					faces = faceCascade.detectMultiScale(grey, 1.3, 5)

					maxArea = 0
					x = 0
					y = 0
					w = 0
					h = 0

					for (_x,_y,_w,_h) in faces:
					    if  _w*_h > maxArea:
						x = int(_x)
						y = int(_y)
						w = int(_w)
						h = int(_h)
						maxArea = w*h

                			if maxArea > 0 :
						tracker.start_track(frame,dlib.rectangle(x-10,y-20,x+w+10,y+h+20))
						trackingFace = True

				if trackingFace:
					trackingQuality = tracker.update(frame)

					if trackingQuality >= 8.75:
						tracked_position =  tracker.get_position()

						t_x = int(tracked_position.left())
						t_y = int(tracked_position.top())
						t_w = int(tracked_position.width())
						t_h = int(tracked_position.height())
						cv2.rectangle(facialFrame,(t_x, t_y),(t_x + t_w , t_y + t_h),rectangleColor ,2)
					else:
						trackingFace = False

				cv2.imshow('Facial Recognition',facialFrame)
				cv2.waitKey(1)
	except Exception as ex:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value,exc_traceback)
		print(ex)
	except KeyboardInterrupt as ex:
		print('KEYBOARD INTERRUPT')
	finally:
		cv2.destroyAllWindows()


def main():
	drone = tellopy.Tello()
	flightControlThread = threading.Thread(target=flightControl,args=(drone,))
	facialRecognitionThread = threading.Thread(target=facialRecognition,args=(drone,))
	try:	
		drone.connect()
	
		drone.wait_for_connection(60.0)
		flightControlThread.start()
		facialRecognitionThread.start()
		flightControlThread.join()
	except Exception as ex:
		print ex
	except KeyboardInterrupt as ex:
		pass
	finally:
		drone.quit()
		
main()


