import pygame
import RPi.GPIO as GPIO
import time

# Initialize the Raspberry Pi GPIO pins
GPIO.setmode(GPIO.BCM)

# Motor 1: Motor 1 forward (GPIO 17), Motor 1 backward (GPIO 18)
# Motor 2: Motor 2 forward (GPIO 22), Motor 2 backward (GPIO 23)
# Motor 3: Motor 3 forward (GPIO 24), Motor 3 backward (GPIO 25)
# Motor 4: Motor 4 forward (GPIO 27), Motor 4 backward (GPIO 28)
motor_pins = {
    "motor1": {"forward": 17, "backward": 18},
    "motor2": {"forward": 22, "backward": 23},
    "motor3": {"forward": 24, "backward": 25},
    "motor4": {"forward": 27, "backward": 28}
}

# Set up the GPIO pins as output
for motor in motor_pins.values():
    GPIO.setup(motor["forward"], GPIO.OUT)
    GPIO.setup(motor["backward"], GPIO.OUT)

# Set up PWM for motor speed control (adjust PWM pins accordingly)
pwm_frequency = 1000  # 1 kHz for motor speed control
motor_pwm = {
    "motor1": GPIO.PWM(motor_pins["motor1"]["forward"], pwm_frequency),
    "motor2": GPIO.PWM(motor_pins["motor2"]["forward"], pwm_frequency),
    "motor3": GPIO.PWM(motor_pins["motor3"]["forward"], pwm_frequency),
    "motor4": GPIO.PWM(motor_pins["motor4"]["forward"], pwm_frequency)
}

# Start PWM with a duty cycle of 0 (motors off)
for pwm in motor_pwm.values():
    pwm.start(0)

# Initialize pygame and the joystick module
pygame.init()
pygame.joystick.init()

# Initialize the Xbox controller
joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Xbox Controller Initialized")

# Helper function to control motor direction and speed
def control_motor(motor, forward, backward, speed):
    if forward:
        GPIO.output(motor["forward"], GPIO.HIGH)
        GPIO.output(motor["backward"], GPIO.LOW)
    elif backward:
        GPIO.output(motor["forward"], GPIO.LOW)
        GPIO.output(motor["backward"], GPIO.HIGH)
    else:
        GPIO.output(motor["forward"], GPIO.LOW)
        GPIO.output(motor["backward"], GPIO.LOW)
    
    motor_pwm[motor]["forward"].ChangeDutyCycle(speed)  # Set motor speed

# Main loop to read controller input and control motors
try:
    while True:
        pygame.event.pump()  # Process any events

        # Read left joystick for motor control
        left_y = joystick.get_axis(1)  # Left Stick Y for forward/backward
        right_y = joystick.get_axis(4)  # Right Stick Y for forward/backward

        # Scale joystick input (range from -1 to 1) to PWM speed (0 to 100)
        motor_speed = int((left_y + 1) * 50)  # Scale to 0-100 for speed control

        # Control motors based on joystick input
        if left_y < 0:  # Move forward
            control_motor("motor1", forward=True, backward=False, speed=motor_speed)
        elif left_y > 0:  # Move backward
            control_motor("motor1", forward=False, backward=True, speed=motor_speed)
        else:  # Stop motor
            control_motor("motor1", forward=False, backward=False, speed=0)

        if right_y < 0:  # Move forward
            control_motor("motor2", forward=True, backward=False, speed=motor_speed)
        elif right_y > 0:  # Move backward
            control_motor("motor2", forward=False, backward=True, speed=motor_speed)
        else:  # Stop motor
            control_motor("motor2", forward=False, backward=False, speed=0)

        # You can add similar controls for motor 3 and motor 4 if needed.

        # Print the input values for recording
        print(f"Left Stick Y: {left_y}, Right Stick Y: {right_y}, Speed: {motor_speed}")

        time.sleep(0.1)  # Delay to make the output readable

except KeyboardInterrupt:
    print("Exiting...")
    pygame.quit()
    GPIO.cleanup()  # Clean up GPIO on exit
