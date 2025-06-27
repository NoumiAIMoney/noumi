import React, { useRef, useState } from 'react';
import { Image, ScrollView, StyleSheet, Text, View } from 'react-native';
import { colors, typography } from '../src/theme';

type Slide = {
  key: string;
  image: any;
  title?: string;
  subtitle?: string;
};

type ImageSliderProps = {
  slides: Slide[];
};

const SLIDE_WIDTH = 370
const SNAP_INTERVAL = SLIDE_WIDTH + 24;

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
          <View key={slide.key}>
            <View style={styles.text}>
                <Text style={styles.title}>{slide.title}</Text>
                <Text style={styles.subtitle}>{slide.subtitle}</Text>
            </View>
            <View style={styles.slide}>
              <View style={styles.imageContainer}>
                <Image
                  source={slide.image}
                  style={styles.image}
                  resizeMode="cover"
                />
              </View>
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
    width: SLIDE_WIDTH,
    height: 306,
    marginRight: 24,
  },
  imageContainer: {
    width: SLIDE_WIDTH,
    height: 306,
    borderRadius: 20,
    overflow: 'hidden',
    backgroundColor: '#fff',
    borderColor: colors.lightPurple,
    borderWidth: 1
  },
  text: {
    paddingBottom: 20,
    width: SLIDE_WIDTH,
  },
  title: {
    fontFamily: typography.fontFamily.semiBold,
    marginTop: 10,
    fontSize: typography.fontSize.XXLarge,
    textAlign: 'left',
    lineHeight: 42,
    letterSpacing: typography.letterSpacing.normal,
    color: colors.black,
    width: '100%'
  },
  subtitle: {
    fontSize: typography.fontSize.body,
    color: colors.black,
    marginBottom: 20,
    textAlign: 'left',
    lineHeight: typography.lineHeight.body,
    fontFamily: typography.fontFamily.medium,
    marginTop: 10,
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
