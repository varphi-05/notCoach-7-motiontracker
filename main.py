# This is a sample Python script.
import cv2
import frame_check as fc
import numpy as np


def nothing(pos):
    pass


# defining the function that stores the pixel being clicked on
def store_click(event, x, y, flags, param):
    global mouseX, mouseY
    if event == cv2.EVENT_LBUTTONDBLCLK:
        mouseX, mouseY = x, y


# defining the function that stores the two points that draw a line
def store_line(event, x, y, flags, param):
    global line, x1, y1
    if event == cv2.EVENT_LBUTTONDOWN:
        x1, y1 = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        if not x1 == x and not y1 == y:
            line = ((x1, y1), (x, y))


# defining the function that stores the colour of a pixel
def store_colour(img, x, y):
    return img[y, x, 2], img[y, x, 1], img[y, x, 0]


# converts a point in a given resolution to a different resolution.
def convert(input_, res_in, res_out):
    return tuple((input_[0] * res_out[0] / res_in[0], input_[1] * res_out[1] / res_in[1]))


# does the same as the above, but converts to data type int instead of float
def int_convert(input_, res_in, res_out):
    return tuple((
        int(input_[0] * res_out[0] / res_in[0]),
        int(input_[1] * res_out[1] / res_in[1])
    ))


if __name__ == '__main__':

    # for Test purposes
    Test = False

    # setting global variables to None
    main_colour, mouseY, mouseX, main_pix, origin, scale, dx, x1, y1 = [None for i in range(9)]

    # list of points that have been tracked
    tracked_points = []

    # introduction and video path input'
    print("--Welcome to the notCoach 7 motion tracker--")
    print("----")
    print("--Copy and paste the path to the video you want to track below--")
    print("--Example path notation: ")
    print("--'C:\\Users\\Japie\\path\\notation\\example.mp4'--")

    if Test:
        vid = cv2.VideoCapture('C:\\Users\\merij\\Desktop\\opencv spul\\blue.mp4')
    else:
        vidpath = str(input("put path here: "))
        vid = cv2.VideoCapture(vidpath)

    # resolution factor input
    print("----")
    print("--Choose the factor by which the standard resolution will be multiplied--")
    print("--so that the program can work faster in the background (or not, if you input 1)--")
    print("--A factor of 0.1 is recommended--")
    res_fac = float(input("put resolution factor here: "))

    frame = True
    first_frame = True
    n_frames = 0
    while True:
        n_frames += 1

        # reads the next frame
        isTrue, frame = vid.read()
        if frame is None:
            break
        # calculates resolutions of both the frames that are shown and the one where the motion tracking happens
        calc_res = (int(frame.shape[1] * res_fac), int(frame.shape[0] * res_fac))
        shown_res = (int(500 * frame.shape[1] / frame.shape[0]), 500)

        # shows warning if frame is not read properly
        if not isTrue:
            print("----")
            print('--Warning: frame not read--')
            break

        # creates the two frames
        shown_frame = cv2.resize(frame, shown_res)
        frame = cv2.resize(frame, calc_res)

        # checks if pixel colour to track is set
        # if so, tracks each pixel to see if it's in the required range
        # then takes an average of the pixels that satisfy and makes it the new pixel colour to track
        if not first_frame:
            # checks for each pixel on the image if the RGB values are in the required range
            # if True, adds the checked pixel in range_pix
            if not shown_range:
                # list of approved pixels
                range_pix = fc.checkframe((0, 0),
                                          (frame.shape[1], frame.shape[0]),
                                          frame,
                                          main_colour,
                                          dx)

            if shown_range:
                cv2.rectangle(shown_frame, shown_range[0], shown_range[1], (0,0,0), 5)

                # list of approved pixels
                range_pix = fc.checkframe(*calc_range, frame, main_colour, dx)
            x_tot, y_tot = 0, 0

            # calculates the center of gravity of all points in range_pix
            # then stores the pixel, and it's colour
            for pix in range_pix:
                x_tot, y_tot = x_tot + pix[0], y_tot + pix[1]
            if len(range_pix):
                main_pix = (x_tot / len(range_pix), y_tot / len(range_pix))
                main_pix_shown = int_convert(main_pix, calc_res, shown_res)
            else:
                print("--Warning: no pixels approved--")

            # creates the new area to search in if chosen to at the start
            if shown_range:
                shown_range = ((int(main_pix_shown[0])-width, int(main_pix_shown[1])-height),
                               (int(main_pix_shown[0])+width, int(main_pix_shown[1])+height))
                calc_range = (int_convert(shown_range[0], shown_res, calc_res),
                              int_convert(shown_range[1], shown_res, calc_res))

            if fc.checkpixel(main_colour,
                          store_colour(frame, int(main_pix[0]), int(main_pix[1])),
                          dx):
                main_colour = store_colour(frame, int(main_pix[0]), int(main_pix[1]))

            # colours all pixels in range_pix so that the user can check if anything goes wrong
            for pix in range_pix:
                shown_frame[
                int_convert(pix, calc_res, shown_res)[1]: int_convert(pix, calc_res, shown_res)[1] + int(
                    1.5 * shown_res[1] / calc_res[1]),
                int_convert(pix, calc_res, shown_res)[0]: int_convert(pix, calc_res, shown_res)[0] + int(
                    1.5 * shown_res[0] / calc_res[0])
                ] = (100, 100, 100)

            cv2.circle(shown_frame, int_convert(main_pix, calc_res, shown_res), 5, (0, 0, 0), 3)

            cv2.imshow('video', shown_frame)

        # checks if this is the first frame of the video
        # if so, this sets the pixel colour to track
        if first_frame:

            # defines k, if at the end of this process k is still ord('r'), this runs again
            k = ord('r')
            while k == ord('r'):

                # deep copies the shown_frame to not colour over it
                first_frame = shown_frame.copy()
                cv2.imshow('video', first_frame)

                # choose a point of axis
                cv2.setMouseCallback('video', store_click)
                print("----")
                print('--First choose the coordinates of your origin by double clicking on the window--')

                # wait's until a point is clicked
                mouseX = None
                while mouseX is None:
                    cv2.waitKey(10)

                # stores the clicked pixel as the origin and show it on the copied frame
                origin = (mouseX, mouseY)
                cv2.circle(first_frame, origin, 5, (0, 255, 0), -1)
                cv2.imshow('video', first_frame)

                cv2.waitKey(500)

                # choosing the scale
                print("----")
                print("--Now choose the scale of the frame by dragging your mouse over the window--")
                print("--The line it creates will be one unit of distance")
                cv2.setMouseCallback('video', store_line)

                # waits until line is drawn
                line = None
                while line is None:
                    cv2.waitKey(10)

                # stores the drawn line and calculates its length in pixels, then show it on the copied frame
                scale = ((line[0][0] - line[1][0]) ** 2 + (line[0][1] - line[1][1]) ** 2) ** 0.5
                cv2.line(first_frame, *line, (0, 0, 255), 3)
                cv2.imshow('video', first_frame)

                cv2.waitKey(100)

                # choosing the first pixel to follow
                cv2.setMouseCallback('video', store_click)
                print("----")
                print("--Thirdly double click on the object you want to track")

                # waits until a point is clicked
                mouseX = None
                while mouseX is None:
                    cv2.waitKey(10)

                # shows the clicked point on the copied frame
                cv2.circle(first_frame, (mouseX, mouseY), 5, (255, 0, 0), -1)
                cv2.imshow('video', first_frame)

                # stores the clicked point and its colour to track
                main_pix = int_convert((mouseX, mouseY), shown_res, calc_res)
                main_colour = store_colour(frame, *main_pix)

                # (optionally) choosing the rectangle in which pixels are checked
                print("----")
                print("--(Optional)--")
                print("--Draw a rectangle in which the algorithm will search for pixel colours--")
                print("--The rectangle's position updates with the position of the tracked object--")
                print("--By changing the slider a preview is given of the rectangle made")
                print("--Press 'c' once the correct values are chosen to continue---")
                print("--Press 's' if you want to skip this step to continue while using the whole frame--")

                # creates a slider for the height and width of the rectangle
                cv2.namedWindow('trackbar')
                cv2.createTrackbar('height', 'trackbar', 0, int(shown_frame.shape[0]), nothing)
                cv2.createTrackbar('width', 'trackbar', 0, int(shown_frame.shape[1]), nothing)

                k = None
                height = 0
                width = 0
                while not k == ord('c') and not k == ord('s'):
                    cv2.imshow('video', first_frame)

                    k = cv2.waitKey(10) & 0xFF

                    # if height or width are updated, colours the outline of the new rectangle
                    height_new = cv2.getTrackbarPos('height', 'trackbar')
                    width_new = cv2.getTrackbarPos('width', 'trackbar')
                    if height_new != height or width_new != width:
                        first_frame = shown_frame.copy()

                        height = height_new
                        width = width_new

                        cv2.circle(first_frame, (mouseX, mouseY), 5, (0, 0, 0), 3)

                        cv2.rectangle(first_frame,
                                      (mouseX - width, mouseY - height),
                                      (mouseX + width, mouseY + height),
                                      (0, 0, 0),
                                      5)
                cv2.destroyWindow('trackbar')
                if k == ord('c'):
                    shown_range = ((mouseX - width, mouseY - height),
                                   (mouseX + width, mouseY + height))
                    calc_range = (int_convert(shown_range[0], shown_res, calc_res),
                                  int_convert(shown_range[1], shown_res, calc_res))
                else:
                    shown_range = False
                    calc_range = False

                # choosing the value for dx
                print("----")
                print("--Choose the range in which pixel colours will be accepted--")
                print("--By changing the slider a preview is given of the pixels that are inside of the range----")
                print("--Press 'c' once the correct value is chosen to continue---")

                # creates a slider for dx
                cv2.namedWindow('trackbar')
                cv2.createTrackbar('dx', 'trackbar', 0, 255, nothing)

                # lets slider be adjustable until 'c' is pressed
                k = None
                dx = 0
                while not k == ord('c'):
                    cv2.imshow('video', first_frame)

                    k = cv2.waitKey(10) & 0xFF

                    # if dx is updated, colours all pixels that are approved under the new range
                    # mostly copied from the method used when first_frame = False
                    dx_new = cv2.getTrackbarPos('dx', 'trackbar')
                    if not dx_new == dx:
                        first_frame = shown_frame.copy()

                        dx = dx_new

                        cv2.circle(first_frame, (mouseX, mouseY), 5, (0, 0, 0), 3)

                        if shown_range:
                            cv2.rectangle(first_frame,
                                          shown_range[0],
                                          shown_range[1],
                                          (0, 0, 0),
                                          5)

                            range_pix = fc.checkframe(*calc_range, frame, main_colour, dx)

                        if not shown_range:
                            range_pix = fc.checkframe((0, 0),
                                                      (frame.shape[1], frame.shape[0]),
                                                      frame,
                                                      main_colour,
                                                      dx)

                        for pix in range_pix:
                            first_frame[
                            int_convert(pix, calc_res, shown_res)[1]: int_convert(pix, calc_res, shown_res)[1] + int(
                                1.5 * shown_res[1] / calc_res[1]),
                            int_convert(pix, calc_res, shown_res)[0]: int_convert(pix, calc_res, shown_res)[0] + int(
                                1.5 * shown_res[0] / calc_res[0])
                            ] = (100, 100, 100)

                # ask if the user wants to redo the data inputs
                print("----")
                print("--Press 'c' to continue and to begin motion tracking--")
                print("--Press 'r' to restart this process and reassign the origin, scale etc.--")

                # if input == c, continues, if input == r, restarts the process under 'if first_frame == True'
                k = None
                while not k == ord('c') and not k == ord('r'):
                    k = cv2.waitKey(10) & 0xFF

                cv2.destroyWindow('trackbar')
                first_frame = False

        # prints and stores the point that is tracked
        # print(tuple(((-1) ** i * (convert(main_pix, calc_res, shown_res)[i] - origin[i]) / scale for i in range(2))))
        tracked_points.append(
            tuple(((-1) ** i * (convert(main_pix, calc_res, shown_res)[i] - origin[i]) / scale for i in range(2)))
        )

        # if q is pressed, stop the program
        if cv2.waitKey(5) == ord('q'):
            print(n_frames)
            break

    # ends the program by destroying all windows
    vid.release()
    cv2.destroyAllWindows()

    # creates the name of the to be saved datasheet
    n = 0
    for i in vidpath:
        n += 1
        if i == '\\':
            last_slash = n
        if i == '.':
            last_dot = n - 1

    # saves the list of tracked points
    np.savetxt(
        vidpath[last_slash:last_dot] + "_motion-track.csv",
        tracked_points,
        delimiter=", ",
        fmt='% s'
    )
    print("saved: " + vidpath[last_slash:last_dot] + "_motion-track.csv")

# task list:
#   -finish taskbar for dx
#   -get qt
#   -add rectangle to limit amount of checked pixels
