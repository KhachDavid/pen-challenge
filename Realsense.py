import pyrealsense2 as rs
import numpy as np
import cv2

class DepthAndColorAligner:
    def __init__(self, args, clipping_distance_in_meters=float('inf')):
        # Create a pipeline
        self.pipeline = rs.pipeline()
        self.args = args
        # Create a config and configure the pipeline to stream
        # different resolutions of color and depth streams
        self.config = rs.config()
        self.clipping_distance_in_meters = clipping_distance_in_meters
        self.clipping_distance = None

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = self.config.resolve(pipeline_wrapper)
        self.device = pipeline_profile.get_device()

        found_rgb = False
        for s in self.device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break
        if not found_rgb:
            raise RuntimeError("The demo requires Depth camera with Color sensor")

        # Enable depth and color streams
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        
        if args.file:
            if args.action == 'r' or args.action == 'read':
                self.config.enable_device_from_file(args.file)
            elif args.action == 'w' or args.action == 'write':
                self.config.enable_record_to_file(args.file)

        # Create an align object
        align_to = rs.stream.color
        self.align = rs.align(align_to)

    def __enter__(self):
        # Start streaming
        self.profile = self.pipeline.start(self.config)

        # Get the depth sensor's depth scale
        depth_sensor = self.profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()
        print("Depth Scale is:", depth_scale)

        # Calculate clipping distance based on scale
        self.clipping_distance = self.clipping_distance_in_meters / depth_scale

        return self

    def process_frames(self):
        # Get frameset of color and depth
        frames = self.pipeline.wait_for_frames()

        # Align the depth frame to color frame
        aligned_frames = self.align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        # Validate that both frames are valid
        if not aligned_depth_frame or not color_frame:
            return None, None

        # Convert depth and color frames to numpy arrays
        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        return depth_image, color_image

    def remove_background(self, depth_image, color_image):
        # Remove background - Set pixels further than clipping_distance to grey
        grey_color = 153
        depth_image_3d = np.dstack((depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
        bg_removed = np.where((depth_image_3d > self.clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)
        return bg_removed

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Stop the pipeline when exiting the context
        self.pipeline.stop()
        cv2.destroyAllWindows()

