import sys
import os
import time
import csv
import numpy as np
import matplotlib.pyplot as plt
import simpleaudio as sa
from datetime import datetime
from Dependencies.ThermalSense import ThermalSense
from ThermalSenseInput import ThermalSenseInput
import json
import queue
import threading

class ThermalSenseRunner:
    def __init__(self, update_callback=None, external_ax=None, external_canvas=None, root=None,
                 mode="default", custom_ranges_dict=None, sample_rate=44100,
                 save_csv=True, save_frame=True, save_sound=True, save_images=True, display_enabled=True):
        self.mode = mode
        self.custom_ranges_dict = custom_ranges_dict
        self.sample_rate = sample_rate
        self.save_csv = save_csv
        self.save_frames = save_frame
        self.save_sound = save_sound
        self.save_images = save_images 
        self.display_enabled = display_enabled
        
        self.thermal_sensor = ThermalSenseInput()
        self.running = False

        self.update_callback = update_callback
        self.ax = external_ax
        self.canvas = external_canvas
        self.root = root
        self.colorbar = None
        self.therm_img = None

        self.start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.result_path = os.path.join(self.base_path, "Results", "ThermalSense", f"ThermalSense-{self.start_time}")
        os.makedirs(self.result_path, exist_ok=True)
        print(f"[DEBUG] Results will be saved to: {self.result_path}")
        if self.save_images:
            os.makedirs(os.path.join(self.result_path, "cleaned"), exist_ok=True)
            os.makedirs(os.path.join(self.result_path, "thermal"), exist_ok=True)

        # Create internal cleaned/thermal folders INSIDE result_path
        self.cleaned_dir = os.path.join(self.result_path, "cleaned")
        self.thermal_dir = os.path.join(self.result_path, "thermal")
        os.makedirs(self.cleaned_dir, exist_ok=True)
        os.makedirs(self.thermal_dir, exist_ok=True)

        self.processor = ThermalSense(
            output_dir=self.result_path,
            mode=self.mode,
            custom_ranges_dict=self.custom_ranges_dict,
            sample_rate=self.sample_rate,
            save_images=self.save_images
        )
        
        self.csv_file_path = os.path.join(self.result_path, f"ThermalSense-{self.start_time}.csv")
        if self.save_csv:
            self._init_csv()
        else:
            self.csv_writer = None
            self.csv_file = None
        
        # ============== OPTIMIZATION: Background I/O Queue ==============
        self.io_queue = queue.Queue()
        self.io_thread = threading.Thread(target=self._io_worker, daemon=True)
        self.io_thread.start()
        
        # ============== OPTIMIZATION: Non-blocking audio ==============
        self.current_audio_play = None
        
        # ============== OPTIMIZATION: CSV buffer ==============
        self.csv_buffer = []
        self.csv_buffer_size = 10  # Flush every 10 frames

    def _init_csv(self):
        self.csv_file = open(self.csv_file_path, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            "frame_number",
            "mean_temperature",
            "heat_range",
            "image_filename",
            "wav_filename",
            "cleaned_image",
            "thermal_image",
            "hot_item_count",
            "cold_item_count",
            "total_item_count"
        ])

    def _get_heat_range(self, temperature):
        if temperature < 10:
            return "very cold"
        elif temperature < 20:
            return "cold"
        elif temperature < 30:
            return "neutral"
        elif temperature < 40:
            return "warm"
        elif temperature < 70:
            return "hot"
        else:
            return "out of range"
    
    # ============== OPTIMIZATION: Background I/O Worker ==============
    def _io_worker(self):
        """Background thread for handling file I/O operations"""
        while True:
            try:
                task = self.io_queue.get(timeout=1)
                if task is None:  # Poison pill to stop thread
                    break
                
                task_type = task['type']
                
                if task_type == 'save_audio':
                    self.processor.save_audio(task['soundscape'], task['path'])
                elif task_type == 'save_image':
                    task['fig'].savefig(task['path'])
                elif task_type == 'flush_csv':
                    if self.csv_writer and not self.csv_file.closed:
                        for row in task['rows']:
                            self.csv_writer.writerow(row)
                        self.csv_file.flush()
                
                self.io_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[I/O Worker Error] {e}")

    def run(self):
        if self.running:
            print("[WARN] Already running. Ignoring duplicate Run request.")
            return
        self.running = True
        
        fig, ax = None, None

        if self.ax and self.canvas:
            ax = self.ax
            fig = self.canvas.figure

            # ============== OPTIMIZATION: Setup plot once, not every frame ==============
            if self.display_enabled:
                # Clear axes once at start
                ax.clear()
                
                # Create thermal image and colorbar ONCE
                self.therm_img = ax.imshow(np.zeros((24, 32)), vmin=0, vmax=60, 
                                          cmap='inferno', interpolation='bilinear')
                
                # Create colorbar only once
                if self.colorbar is None:
                    self.colorbar = fig.colorbar(self.therm_img, ax=ax, fraction=0.046, pad=0.04)
                
                fig.subplots_adjust(bottom=0.2)
                
                # Create text labels once
                self.hot_label = ax.text(0.01, -0.08, '', color='red', transform=ax.transAxes)
                self.cold_label = ax.text(0.3, -0.08, '', color='blue', transform=ax.transAxes)
                self.total_label = ax.text(0.6, -0.08, '', color='white', transform=ax.transAxes)
                
                self.canvas.draw()
            else:
                # Create dummy references for backend processing
                self.therm_img = None
                self.colorbar = None
                self.hot_label = None
                self.cold_label = None
                self.total_label = None

        frame = np.zeros((24 * 32,))
        frame_number = 0
        t_array = []

        print("Starting ThermalSenseRunner real-time processing... (Press Ctrl+C to exit safely)")

        try:
            while self.running:
                t1 = time.monotonic()
                
                # Get frame from sensor
                self.thermal_sensor.mlx.getFrame(frame)
                data_array = np.reshape(frame, (24, 32))

                # Update callback if provided
                if self.update_callback:
                    try:
                        self.update_callback(data_array)
                    except Exception as e:
                        print(f"[Live callback Error] {e}")

                if not self.running:
                    break
                
                # ============== OPTIMIZATION: Update display efficiently ==============
                if self.display_enabled and self.therm_img is not None:
                    # Update image data
                    self.therm_img.set_data(np.fliplr(data_array))
                    self.therm_img.set_clim(vmin=np.min(data_array), vmax=np.max(data_array))
                    
                    # Update colorbar range (no need to recreate)
                    if self.colorbar:
                        self.colorbar.update_normal(self.therm_img)

                # Calculate FPS
                t_array.append(time.monotonic() - t1)
                if len(t_array) > 30:  # Keep last 30 samples
                    t_array.pop(0)
                print(f"Sample Rate: {len(t_array) / np.sum(t_array):.1f} fps")

                mean_temperature = np.mean(data_array)
                print(f"[Frame {frame_number}] Mean temperature: {mean_temperature:.2f} C")

                # Process image
                cleaned, soundscape = self.processor.process_image(data_array)

                # Get thresholds on first frame
                if frame_number == 0:
                    rngs = list(self.processor.get_active_ranges().values())
                    edges = sorted({lo for (lo, _), *_ in rngs} |
                                  {hi for (_, hi), *_ in rngs})
                    self.hot_thr = edges[-2] if len(edges) >= 2 else 30.0
                    self.cold_thr = edges[1] if len(edges) >= 2 else 20.0
                    print(f"[DEBUG] hot_thr={self.hot_thr}  cold_thr={self.cold_thr}")

                # Count hot/cold regions
                hot_count, cold_count = self.processor.detect_hot_cold_regions(
                    cleaned, self.hot_thr, self.cold_thr)
                total_items = hot_count + cold_count

                # Update GUI labels
                if self.display_enabled and self.hot_label:
                    self.hot_label.set_text(f"Hot: {hot_count}")
                    self.cold_label.set_text(f"Cold: {cold_count}")
                    self.total_label.set_text(f"Total: {total_items}")
                    
                    # ============== OPTIMIZATION: Single draw call ==============
                    if self.canvas and self.root:
                        self.canvas.draw_idle()  # Non-blocking
                        self.root.update_idletasks()  # Process pending events

                # ============== OPTIMIZATION: Non-blocking audio playback ==============
                wav_filename = f"frame_{frame_number:03d}.wav"
                wav_path = os.path.join(self.result_path, wav_filename)
                
                if self.save_sound:
                    # Queue audio save in background
                    self.io_queue.put({
                        'type': 'save_audio',
                        'soundscape': soundscape.copy(),  # Copy to avoid race conditions
                        'path': wav_path
                    })
                
                # Play audio non-blocking
                self.play_audio_nonblocking(wav_path)

                # ============== OPTIMIZATION: Queue image save in background ==============
                image_filename = f"frame_{frame_number:03d}.png"
                image_path = os.path.join(self.result_path, image_filename)
                
                if self.save_frames and fig:
                    self.io_queue.put({
                        'type': 'save_image',
                        'fig': fig,
                        'path': image_path
                    })

                cleaned_path = os.path.join(self.result_path, "cleaned", image_filename)
                thermal_path = os.path.join(self.result_path, "thermal", image_filename)

                # ============== OPTIMIZATION: Buffer CSV writes ==============
                if self.csv_writer and not self.csv_file.closed:
                    self.csv_buffer.append([
                        frame_number,
                        mean_temperature,
                        self._get_heat_range(mean_temperature),
                        image_filename,
                        wav_filename,
                        cleaned_path,
                        thermal_path,
                        hot_count,
                        cold_count,
                        total_items
                    ])
                    
                    # Flush buffer periodically
                    if len(self.csv_buffer) >= self.csv_buffer_size:
                        self.io_queue.put({
                            'type': 'flush_csv',
                            'rows': self.csv_buffer.copy()
                        })
                        self.csv_buffer.clear()

                frame_number += 1
                
                # ============== OPTIMIZATION: Removed time.sleep(1) ==============
                # Let the sensor dictate the frame rate instead of artificial delay

        except KeyboardInterrupt:
            print("KeyboardInterrupt detected. Stopping safely...")
            self.stop()

        print("ThermalSense stopped.")

    def stop(self):
        if not self.running:
            return
        
        self.running = False
        
        # Flush remaining CSV buffer
        if self.csv_buffer and self.csv_writer and not self.csv_file.closed:
            for row in self.csv_buffer:
                self.csv_writer.writerow(row)
            self.csv_file.flush()
            self.csv_buffer.clear()
        
        # Stop audio playback
        if self.current_audio_play and self.current_audio_play.is_playing():
            self.current_audio_play.stop()
        
        # Stop I/O worker thread
        self.io_queue.put(None)  # Poison pill
        self.io_thread.join(timeout=2)
        
        # Clean up matplotlib
        self.colorbar = None
        self.therm_img = None
        plt.close('all')
        
        # Close CSV file
        if self.csv_file and not self.csv_file.closed:
            self.csv_file.close()
        
        print("CSV saved at:", self.csv_file_path)

    def play_audio_nonblocking(self, wav_path):
        """Non-blocking audio playback"""
        try:
            # Stop previous audio if still playing
            if self.current_audio_play and self.current_audio_play.is_playing():
                self.current_audio_play.stop()
            
            # Check if file exists (may not be saved yet if queued)
            if os.path.exists(wav_path):
                wave_obj = sa.WaveObject.from_wave_file(wav_path)
                self.current_audio_play = wave_obj.play()
                # Don't wait - let it play in background!
        except Exception as e:
            print(f"Error playing audio: {e}")


if __name__ == "__main__":
    runner = ThermalSenseRunner()
    runner.run()
