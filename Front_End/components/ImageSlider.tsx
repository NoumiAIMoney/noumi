import React, { useRef, useState } from 'react';
import { View, StyleSheet, ScrollView, Image } from 'react-native';
import { colors } from '../src/theme';

type Slide = {
  key: string;
  image: any;
};

type ImageSliderProps = {
  slides: Slide[];
};

const SNAP_INTERVAL = 320 + 24;

export default function ImageSlider({ slides }: ImageSliderProps) {
  const scrollRef = useRef<ScrollView>(null);
  const [index, setIndex] = useState(0);

  const onScroll = (e: any) => {
    const i = Math.round(e.nativeEvent.contentOffset.x / SNAP_INTERVAL);
    setIndex(i);
  };

  return (
    <>
      <ScrollView
        ref={scrollRef}
        horizontal
        snapToInterval={SNAP_INTERVAL}
        decelerationRate="fast"
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={{ paddingHorizontal: 0 }}
        onScroll={onScroll}
        scrollEventThrottle={16}
      >
        {slides.map((slide) => (
          <View key={slide.key} style={styles.slide}>
            <View style={styles.imageContainer}>
              <Image
                source={slide.image}
                style={styles.image}
                resizeMode="cover"
              />
            </View>
          </View>
        ))}
      </ScrollView>


      <View style={styles.dots}>
        {slides.map((_, i) => (
          <View
            key={i}
            style={[styles.dot, i === index && styles.dotActive]}
          />
        ))}
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  slide: {
    width: 320,
    height: 306,
    marginRight: 24,
  },
  imageContainer: {
    width: 320,
    // not 308 because the first picture does not fit it perfectly
    // can ask for the asset to have the exact size
    height: 306,
    borderRadius: 20,
    overflow: 'hidden',
    backgroundColor: '#fff',
    borderColor: colors.lightPurple,
    borderWidth: 1
  },
  image: {
    width: '100%',
    height: '100%',
  },
  dots: {
    marginVertical: 20,
    flexDirection: 'row',
    justifyContent: 'center',
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#CCC',
    margin: 4,
  },
  dotActive: {
    backgroundColor: '#593F90',
  },
});
