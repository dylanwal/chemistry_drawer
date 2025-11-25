# Change Log

## Version 0.0.8
#### Motivation for changes:

* Plotting large grids of molecules was SLOW!
  * The main bottleneck was Plotly not the code the repo. The previous workaround (generating individual images with Pillow and stitching them together) 
  remained but this was still too slow for my liking.
* Fix several structure bugs:
  * charges
  * double bonds around rings


#### Solution:
* Backend Agnosticism: The backend was fully overhauled to support multiple plotting libraries, rather than relying solely on Plotly.
  * Most work in this version was adding Matplotlib. Plotly is still supported, but is slower.
* Matplotlib Integration: We successfully implemented Matplotlib generation. This reduced the time required to generate SVGs for 1,000 molecules from 20 minutes down to 7 seconds.
* New Styling System: Replaced config with StyleTemplate, streamlining the process of switching between styles and plotting methods.

#### Challenges & Limitations:
* Font Scaling: A persistent challenge is the autoscaling of text. Because Plotly and Matplotlib handle font sizes 
differently, predicting textbox dimensions is difficult. While the style sheet parameters have been tuned to adjust 
for this, a perfect solution for dynamic text scaling is still in development.
  * Another hope of the re-write was to get Plotly molecules we could interact with, but with the text scaling issue
  this remains just a dream. 