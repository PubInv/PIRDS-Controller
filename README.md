# PIRDS-Controller
A hardware device for viewing PIRDS data, possibly with added control, with some Raspi Software.

## Basic Idea

This project is closely associated with the Freespireco project, and the [VentMon](https://github.com/PubInv/ventmon-ventilator-inline-test-monitor) in particular, although it can really be used with any PIRDS-producing device.

The idea is to use a Raspberry PI, with Docker, the Raspberry Pi 7" Touchscreen Display, and the Smart Pi Touch 2 case to produce 
stand-alone unit that can display PIRDS data with the VentDisplay software. Additionally, we plan a mounting bracket so that the 
Physical VentMon can be mounted onto the case in a removable way (possibly with zip-ties), creating a "molecule" that act as a 
standalong Ventilation Monitor/Tester.

## The VentMon and the Touch Screen

Here is a photo showing the VentMon and the Touchscreen.

![IMG-2369](https://user-images.githubusercontent.com/5296671/120369837-7a458400-c2d9-11eb-8713-eebb2bcd9166.JPG)

## The Bracket

Because we need room for the air hoses and it is better to have the air hoses go from left to right, we mount the VentMon behind and to the size of the main display. It could be placed completely behind the touchscreen, but then you would not be able to adjust the angle of the screen, mount the touch screen on a wall, or see the OLED on the VentMon, all of which are advantages. However, this mounting approach has the disadvantage of making the combined device a bit larger.

The photos below show a basic design for a flat-ish bracket that could mount the VentMon to VESA MIS-D 75 mounts on the the TFT screen 

![IMG-2371](https://user-images.githubusercontent.com/5296671/120370164-db6d5780-c2d9-11eb-8273-b9d5dbb25f09.JPG)
![IMG-2370](https://user-images.githubusercontent.com/5296671/120370170-dd371b00-c2d9-11eb-97ef-190c67fdf43b.JPG)

This design is currently imperfect, because it would be a Bezel in front of the VentMon. Additionaly thought and modifications are required before we would try to laser cut such a piece. In pariticular, how we would hould the corner brackets is completely unclear.



