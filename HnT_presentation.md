---- .aligncenter .bg-black
@unsplash(J39X2xX_8CQ) .dark

.text-data **Girls, Interrupted**
 @h4 A computational study of gender in the movies.
 
@footer
 @div .wrap @div .span
  @button(href="https://github.com/thoppe/Girls-Interrupted") .alignleft .ghost
   ::github:: github.com/thoppe/Girls-Interrupted
  @button(href="https://twitter.com/metasemantic") .ghost .alignright
   ::twitter:: @metasemantic 


---- .aligncenter .bg-black
@unsplash(4SLz_RCk6kQ) .dark


@h1 _Q: Is there a gender disparity in Hollywood?_
@h4 If so, how much? Can we quantifiy it?

<br><br><br>

@h2 Does this change over time?
@h2 Do some movies have more faces than others?

<br><br><br>

@h2 What does it mean to measure gender?
@h4 We can only measure gender "expression",
@h4 a model trained on **images** of males and females.

-------
@background_video(url="spectrum_quick.mp4")


----- .bg-white .aligncenter .slide-top
@unsplash(ny-lHmsHYHk)
@h1 175 movies. 1 frame per second.
@h4 Each face must occupy at least 0.15% of the screen.

----- .bg-white .aligncenter

.left @h3 12 Angry Men
@img(src="figures/lineplots/12.Angry.Men.1957.DVDRip.x264-DJ.mkv.png")

.right @h3 2001 A Space Odyssey
@img(src="figures/lineplots/2001.A.Space.Odyssey.1968.DVDRip.x264-DJ.mkv.png")

.left @h3 Clueless
@img(src="figures/lineplots/Clueless.1995.BluRay.720p.H264.mp4.png")

.right @h3 Fifty Shades of Grey
@img(src="figures/lineplots/Fifty.Shades.of.Grey.2015.BDRip.x264-DJ.mkv.png")

.left @h3 Girl Interrupted
@img(src="figures/lineplots/Girl.Interrupted.1999.WEB-DL.720p.H264.mp4.png")

.right @h3 The Godfather
@img(src="figures/lineplots/The.Godfather.1972.720p.bluray.x264.mkv.png")

----- .bg-white .aligncenter

@h2 All movies, colored by year. 1930's (blue) to 2017 (red)

.aligncenter
   @img(src="docs/figures/ratio_plot_empty.png" width=700px)
   @img(src="docs/figures/ratio_plot_years.png" width=700px)

Four zones: Old Hollywood, girl comedies, "romance", and male heavy action or landscapes

----- .bg-white .aligncenter

@h2 Male zone (note the axis!), female comedy zone

.aligncenter
   @img(src="docs/figures/ratio_plot_males.png" width=700px)
   @img(src="docs/figures/ratio_plot_females.png" width=700px)

----- .bg-white  .aligncenter

@h2 Rise of the "blockbuster"
@figure(src="docs/figures/barplot_yearsVsFaceAndFemales.png" )

----- .bg-white .aligncenter
@h1 **Fargo** (1996)
.aligncenter
  @img(src="figures/tSNE/points/Fargo.1996.REMASTERED.BluRay.720p.H264.mp4.png" width=700) @img(src="figures/tSNE/images/Fargo.1996.REMASTERED.BluRay.720p.H264.mp4.png" width=700)

tSNE plots using facial detection landmarks

----- .bg-white .aligncenter
@h1 **Inception** (2010)
.aligncenter
  @img(src="figures/tSNE/points/Inception.2010.DVDRip.x264-DJ.mkv.png" width=700) @img(src="figures/tSNE/images/Inception.2010.DVDRip.x264-DJ.mkv.png" width=700)

tSNE plots using facial detection landmarks

----- .bg-white .aligncenter
@h1 **Rebecca** (1940)
.aligncenter
  @img(src="figures/tSNE/points/Rebecca.1940.BluRay.720p.H264.mp4.png" width=700) @img(src="figures/tSNE/images/Rebecca.1940.BluRay.720p.H264.mp4.png" width=700)

tSNE plots using facial detection landmarks

----- .bg-white .aligncenter
@h1 **LotR: The Fellowship of the Rings** (2001)
.aligncenter
  @img(src="figures/tSNE/points/The.Lord.of.the.Rings.The.Fellowship.of.the.Ring.2001.BDRip.x264-DJ.mkv.png" width=700) @img(src="figures/tSNE/images/The.Lord.of.the.Rings.The.Fellowship.of.the.Ring.2001.BDRip.x264-DJ.mkv.png" width=700)

tSNE plots using facial detection landmarks

-----
@background(src="docs/figures/ratio_plot_titles.png")
HI!