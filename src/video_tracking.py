import os
import sys

import cv2
import pandas as pd
import math

from ultralytics import YOLO
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.vision_utils import get_video_creation_time, extract_and_convert_create_date

def analyze_and_save_ants_movements(model_path, masked_path, output_directory, save_excel=False, save_video=False):
    # Load the YOLO model
    model = YOLO(model_path)
    # Set up video capture
    cap = cv2.VideoCapture(masked_path)

    # Extract video name and construct output paths
    video_name = os.path.basename(masked_path)
    parent_dir = os.path.dirname(masked_path)
    # season = parent_dir.split('/')[-3]
    # location = parent_dir.split('/')[-2]
    # camera = parent_dir.split('/')[-1]
    excel_filename = f"{video_name.split('.')[0]}_object_tracking_results.xlsx"
    output_excel_path = os.path.join(output_directory, excel_filename)
    output_video_filename = f"{video_name.split('.')[0]}_detections.mov"
    output_video_path = os.path.join(output_directory, output_video_filename)

    # Retrieve original video path and creation date
    original_video_name = video_name.replace('masked_', '').replace('.mov', '.MOV')
    original_video_path = os.path.join(parent_dir, original_video_name)
    creation_date = get_video_creation_time(original_video_path)
    creation_date = extract_and_convert_create_date(creation_date)

    # Initialize data structures
    frame_object_count = pd.DataFrame(columns=['Frame', 'Unique Object Count'])
    object_frame_count = {}
    object_distances = {}
    confidence_threshold = 0.5

    # Get frame dimensions and center
    ret, frame = cap.read()
    if not ret:
        print("Error reading video file.")
        cap.release()
        return
    frame_height, frame_width = frame.shape[:2]
    frame_center = (frame_width // 2, frame_height // 2)

    # Set up video writer if saving video
    if save_video:
        fps = cap.get(cv2.CAP_PROP_FPS)
        video_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    # Process video frames
    frame_number = 0
    while ret:
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1
        results = model.track(frame, persist=True)
        detections = results[0].boxes
        unique_ids_in_frame = set()

        for result in detections:
            conf = result.conf.item()
            if conf < confidence_threshold:
                continue

            try:
                obj_id = int(result.id.item())
                unique_ids_in_frame.add(obj_id)
                if obj_id in object_frame_count:
                    object_frame_count[obj_id] += 1
                else:
                    object_frame_count[obj_id] = 1

                x1, y1, x2, y2 = result.xyxy[0].tolist()
                bbox_center = ((x1 + x2) // 2, (y1 + y2) // 2)
                distance_from_center = math.sqrt((bbox_center[0] - frame_center[0]) ** 2 + (bbox_center[1] - frame_center[1]) ** 2)

                if obj_id in object_distances:
                    object_distances[obj_id].append(distance_from_center)
                else:
                    object_distances[obj_id] = [distance_from_center]

                # Draw bounding boxes and labels on the frame
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                label = f'ID {obj_id} Conf: {conf:.2f}'
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            except:
                continue

        # Update unique object count per frame
        frame_object_count = frame_object_count.append(
            {'Frame': frame_number, 'Unique Object Count': len(unique_ids_in_frame)}, ignore_index=True
        )

        # Save annotated frame to video if save_video is True
        if save_video:
            video_writer.write(frame)

        # Display frame (optional)
        cv2.imshow('frame', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    if save_video:
        video_writer.release()
    cv2.destroyAllWindows()

    # Generate and save Excel statistics if save_excel is True
    if save_excel:
        movement_data = []
        for obj_id, distances in object_distances.items():
            first_distance = sum(distances[:5]) / min(5, len(distances))
            last_distance = sum(distances[-5:]) / min(5, len(distances))
            movement = 'Closer' if last_distance < first_distance else 'Further'
            movement_data.append((obj_id, movement))

        object_frame_count_df = pd.DataFrame(list(object_frame_count.items()), columns=['Object ID', 'Frame Count'])
        movement_df = pd.DataFrame(movement_data, columns=['Object ID', 'Movement'])
        final_df = pd.merge(object_frame_count_df, movement_df, on='Object ID')
        final_df = final_df[final_df['Frame Count'] > 30]

        total_frames = final_df['Frame Count'].sum()
        closer_frames = final_df[final_df['Movement'] == 'Closer']['Frame Count'].sum()
        further_frames = final_df[final_df['Movement'] == 'Further']['Frame Count'].sum()
        proportion_closer = closer_frames / total_frames if total_frames > 0 else 0
        proportion_further = further_frames / total_frames if total_frames > 0 else 0
        average_ants_per_frame = frame_object_count['Unique Object Count'].mean()

        with pd.ExcelWriter(output_excel_path) as writer:
            frame_object_count.to_excel(writer, sheet_name='Frame Object Count', index=False)
            final_df.to_excel(writer, sheet_name='Object Frame Count and Movement', index=False)
            pd.DataFrame({
                'Metric': ['Proportion of Closer', 'Proportion of Further'],
                'Value': [proportion_closer, proportion_further]
            }).to_excel(writer, sheet_name='Proportions', index=False)
            pd.DataFrame({
                'Metric': ['Average Ants per Frame'],
                'Value': [average_ants_per_frame]
            }).to_excel(writer, sheet_name='Average Ants per Frame', index=False)
            pd.DataFrame({
                'original_video_path': [original_video_path],
                'creation_date': [creation_date]
            }).to_excel(writer, sheet_name='Original Video Info', index=False)

        print(f"Results have been saved to {output_excel_path}")

    if save_video:
        print(f"Annotated video has been saved to {output_video_path}")



if __name__ == "__main__":
    # example for using the code in case of just running the file
    # analyze_and_save_ants_movements('/path/to/model.pt', "/path/to/video.mov", "/output/dir/")

    # example for using the code in case of parallel running
    # video_path = sys.argv[1]
    # output_dir = sys.argv[2]
    # analyze_and_save_ants_movements('/path/to/model.pt', video_path, output_dir)



