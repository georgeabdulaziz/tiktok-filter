/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 */

import React, { useState } from 'react';
import type { PropsWithChildren } from 'react';
import {
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  useColorScheme,
  View,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import Video from 'react-native-video';
import { launchImageLibrary } from 'react-native-image-picker';

import {
  Colors,
  DebugInstructions,
  Header,
  LearnMoreLinks,
  ReloadInstructions,
} from 'react-native/Libraries/NewAppScreen';

type SectionProps = PropsWithChildren<{
  title: string;
}>;

function Section({ children, title }: SectionProps): React.JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';
  return (
    <View style={styles.sectionContainer}>
      <Text
        style={[
          styles.sectionTitle,
          {
            color: isDarkMode ? Colors.white : Colors.black,
          },
        ]}>
        {title}
      </Text>
      <Text
        style={[
          styles.sectionDescription,
          {
            color: isDarkMode ? Colors.light : Colors.dark,
          },
        ]}>
        {children}
      </Text>
    </View>
  );
}

function App(): React.JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [watermarkDetected, setWatermarkDetected] = useState<boolean | null>(null);
  const [processedVideo, setProcessedVideo] = useState<string | null>(null);

  const backgroundStyle = {
    backgroundColor: isDarkMode ? Colors.darker : Colors.lighter,
  };

  const handleVideoPick = async () => {
    try {
      const result = await launchImageLibrary({
        mediaType: 'video',
        videoQuality: 'high',
        selectionLimit: 1,
      });

      if (result.assets && result.assets[0]) {
        setSelectedVideo(result.assets[0].uri);
      }
    } catch (err) {
      console.error('Error picking video:', err);
    }
  };

  const handleProcessVideo = async () => {
    if (!selectedVideo) return;

    setIsProcessing(true);
    try {
      // Create form data
      const formData = new FormData();
      formData.append('video', {
        uri: selectedVideo,
        type: 'video/mp4',
        name: 'video.mp4',
      } as any);

      const response = await fetch('http://10.0.2.2:5000/process-video', {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to process video');
      }

      const data = await response.json();
      setWatermarkDetected(data.watermark_detected);
      
      // Update the processed video URL handling
      if (data.processed_video_url) {
        // Ensure the URL is properly formatted
        const baseUrl = 'http://10.0.2.2:5000';
        const videoUrl = data.processed_video_url.startsWith('/') 
          ? data.processed_video_url 
          : `/${data.processed_video_url}`;
        setProcessedVideo(`${baseUrl}${videoUrl}`);
      }
    } catch (err) {
      console.error('Error processing video:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <View style={[backgroundStyle, styles.container]}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={backgroundStyle.backgroundColor}
      />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>TikTok Watermark Remover</Text>
        </View>

        <View style={styles.content}>
          <TouchableOpacity
            style={styles.button}
            onPress={handleVideoPick}
          >
            <Text style={styles.buttonText}>
              {selectedVideo ? 'Change Video' : 'Select Video'}
            </Text>
          </TouchableOpacity>

          {selectedVideo && (
            <View style={styles.videoContainer}>
              <Video
                source={{ uri: selectedVideo }}
                style={styles.video}
                resizeMode="contain"
                controls
              />
            </View>
          )}

          {selectedVideo && !isProcessing && (
            <TouchableOpacity
              style={styles.button}
              onPress={handleProcessVideo}
            >
              <Text style={styles.buttonText}>Process Video</Text>
            </TouchableOpacity>
          )}

          {isProcessing && (
            <View style={styles.processingContainer}>
              <ActivityIndicator size="large" color="#0000ff" />
              <Text style={styles.processingText}>Processing video...</Text>
            </View>
          )}

          {watermarkDetected !== null && (
            <View style={styles.resultContainer}>
              <Text style={styles.resultText}>
                Watermark {watermarkDetected ? 'Detected' : 'Not Detected'}
              </Text>
            </View>
          )}

          {processedVideo && (
            <View style={styles.videoContainer}>
              <Text style={styles.sectionTitle}>Processed Video</Text>
              <Video
                source={{ uri: processedVideo }}
                style={styles.video}
                resizeMode="contain"
                controls
              />
            </View>
          )}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  sectionContainer: {
    marginTop: 32,
    paddingHorizontal: 24,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: '600',
  },
  sectionDescription: {
    marginTop: 8,
    fontSize: 18,
    fontWeight: '400',
  },
  highlight: {
    fontWeight: '700',
  },
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
  },
  header: {
    marginTop: 100,
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  content: {
    padding: 20,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginVertical: 10,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  videoContainer: {
    marginVertical: 20,
    width: '100%',
    aspectRatio: 16 / 9,
  },
  video: {
    flex: 1,
  },
  processingContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  processingText: {
    marginTop: 10,
    fontSize: 16,
  },
  resultContainer: {
    marginVertical: 20,
    padding: 15,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  resultText: {
    fontSize: 18,
    textAlign: 'center',
  },
});

export default App;
