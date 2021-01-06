#!/bin/python3.7

import cv2
import numpy as np


MAX_FEATURES = 500
GOOD_MATCH_PERCENT = 0.15


def alignImages(im1, im2):

  # Convert images to grayscale
  im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
  im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

  # Detect ORB features and compute descriptors.
  orb = cv2.ORB_create(MAX_FEATURES)
  keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
  keypoints2, descriptors2 = orb.detectAndCompute(im2Gray, None)

  # Match features.
  matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
  matches = matcher.match(descriptors1, descriptors2, None)

  # Sort matches by score
  matches.sort(key=lambda x: x.distance, reverse=False)

  # Remove not so good matches
  numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
  matches = matches[:numGoodMatches]

  # Extract location of good matches and filter by diffy
  points1 = np.zeros((len(matches), 2), dtype=np.float32)
  points2 = np.zeros((len(matches), 2), dtype=np.float32)

  for i, match in enumerate(matches):
    points1[i, :] = keypoints1[match.queryIdx].pt
    points2[i, :] = keypoints2[match.trainIdx].pt


  # filter points by using mask
  matches_Mask = [[0,0] for i in range(len(matches))]
  for i in range(len(matches)):
      pt1 = points1[i]
      pt2 = points2[i]
      pt1x, pt1y = zip(*[pt1])
      pt2x, pt2y = zip(*[pt2])
      diffy = np.float32( np.float32(pt2y) - np.float32(pt1y) )
      print(diffy)
      if abs(diffy) < 10.0:
        matches_Mask[i]=[1,0]  #<--- mask created
  print(matches_Mask)

  draw_params = dict(matchColor = (255,0,),
    singlePointColor = (255,255,0),
    matchesMask = matches_Mask, #<---- remove mask here
    flags = 0)

  # Draw top matches
  imMatches = cv2.drawMatches(im1, keypoints1, im2, keypoints2, matches, None, **draw_params)
  cv2.imwrite("/Users/fred/desktop/lena_matches.png", imMatches)


  # Find Affine Transformation
  # true means full affine, false means rigid (SRT)
  m = cv2.estimateRigidTransform(points1,points2,False)

  # Use affine transform to warp im1 to match im2
  height, width, channels = im2.shape
  im1Reg = cv2.warpAffine(im1, m, (width, height))

  return im1Reg, m


if __name__ == '__main__':

  # Read reference image
  refFilename = r"D:\Ynby\Git\Image-Mosaicing-master\input\mouth\videomouth2/mouth_1.jpg"
  print("Reading reference image : ", refFilename)
  imReference = cv2.imread(refFilename, cv2.IMREAD_COLOR)

  # Read image to be aligned
  imFilename = r"D:\Ynby\Git\Image-Mosaicing-master\input\mouth\videomouth2/mouth_2.jpg"
  print("Reading image to align : ", imFilename);
  im = cv2.imread(imFilename, cv2.IMREAD_COLOR)

  print("Aligning images ...")
  # Registered image will be stored in imReg.
  # The estimated transform will be stored in m.
  imReg, m = alignImages(im, imReference)

  # Write aligned image to disk.
  outFilename = r"D:\Ynby\Git\Image-Mosaicing-master\input\mouth\videomouth2/results/mouth_orb.jpg"
  print("Saving aligned image : ", outFilename);
  cv2.imwrite(outFilename, imReg)

  # Print estimated homography
  print("Estimated Affine Transform : \n",  m)
