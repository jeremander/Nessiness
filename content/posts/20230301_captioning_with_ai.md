Title: Adding Captions to Video with AI
Category: Machine Learning
Tags: AI, Machine Learning, Python, video
Summary: Using OpenAI Whisper and `ffmpeg` to add captions to your videos.

Hi all! After a long hiatus, this is my first "real" blog post with actual content. 😆

In this day and age, [web accessibility](https://www.w3.org/WAI/fundamentals/accessibility-intro/) is all but essential, and captioning video is a key part of that. Platforms like YouTube will now caption uploaded videos by default in most circumstances, but sometimes you may be working with other platforms or creating your own videos, so you'll need to create the captions yourself.

Last weekend my friend who's a music teacher asked me for help adding captions to a video, for the benefit of a hearing-impaired student. A quick Google search brought up many web-based services that use machine learning to generate captions from audio, but these tended to require registration and limit the features available without a monthly subscription (for example, video duration).

Since I fancy myself a command-line warrior, and since it seemed onerous to upload/download a video just to edit it, I sought a more efficient solution. Searching Github led me to an elegant Python package called [auto-subtitle](https://github.com/m1guelpf/auto-subtitle).

`auto-subtitle` makes use of OpenAI's [Whisper](https://openai.com/research/whisper) system for automatic speech recognition and translation (yes, that's the same OpenAI who brought us [ChatGPT](https://chat.openai.com)). Below I'll go through the steps of how I used this tool to create video captions.

## Step 0: Install auto-subtitle

Follow the install instructions on the Github [page](https://github.com/m1guelpf/auto-subtitle).

(__NOTE__: I had trouble installing it using Python 3.11, which is apparently too new to support PyTorch; I got around this by reverting to Python 3.9 using [pyenv](https://github.com/pyenv/pyenv)).

## Step 1: Generate captions

Let's say we have a video we want to caption. As a test example, I downloaded [this video](https://www.youtube.com/watch?v=CGmfGaZecHA), naming it `video.mp4`.

To caption it with Whisper AI, it took just a single command:

```plaintext
auto_subtitle video.mp4 -o caption --output_srt True --verbose True
```

I provided the name of the video and an output directory. I also added some flags, `--output_srt True` to save the subtitle file (more on that later), and `--verbose True` to have the program print info as it runs.

Here is what it printed out:

```plaintext
Extracting audio from video...
Generating subtitles for video... This might take a while.
Detecting language using up to the first 30 seconds. Use
`--language` to specify the language
Detected language: English
[00:00.000 --> 00:06.120]  Hello everyone. In this lesson about
the origins of the orchestra, we will be looking
[00:06.120 --> 00:11.440]  at the types of music that appeared
during the Baroque era.
[00:11.440 --> 00:18.080]  Music and many other art forms began
to flourish between 1600 and 1750, during a time we now
[00:18.080 --> 00:25.520]  call the Baroque era. In the early
1600s, theatre was big in England, where Shakespeare
...
```

This took about a minute to run (the video was 3.5 minutes). Verbose mode was very helpful since it let me monitor the speed and accuracy of the transcription as it progressed. Two files were saved in the `caption` folder, `video.mp4` (captioned version) and `video.srt`.

As you can see from the sample above, the quality of the transcription is impeccable, as one might expect of OpenAI's recent cutting-edge language models. I was particularly impressed with how well it did on proper names, and it also seemed to be completely robust to ambient noise and music (this test video plays light orchestral music throughout).

`auto-subtitle` is also capable of doing translation from other languages into English, but I have not yet tested this out in depth.

## Step 2: Fix up mistakes

Although the language model can transcribe speech almost perfectly, there may still be some minor errors to fix up. If you're in a hurry and don't care about perfection, you can take the auto-generated video and go about your day. But if you want to make some tweaks, there are a couple approaches:

1. Use a subtitle editing program (for example, [Subtitle Edit](https://www.nikse.dk/subtitleedit), which seems pretty good). This lets you edit subtitles while watching the video in real time.

2. Edit the `.srt` subtitle file in a text editor, then combine it with the original video.

I went with option #2.

The SRT file format is dead simple. It's just a text file containing caption text segments, along with their time ranges:

```srt
1
0:00:00.000 --> 0:00:06.120
Hello everyone. In this lesson about the origins of the orchestra,
we will be looking

2
0:00:06.120 --> 0:00:11.440
at the types of music that appeared during the Baroque era.

3
0:00:11.440 --> 0:00:18.080
Music and many other art forms began to flourish between 1600 and
1750, during a time we now

...
```

As I said earlier, the transcription of this video was near-perfect. The _very minor_ issues I had were:

1. Punctuation errors. In particular, some sentences were wanting commas.

2. A couple of typos on the "rarer" musical terms. Namely, "bourrée" was spelled "beret," and "gigue" was "gig." But it had no problem with names like Monteverdi and Versailles. (Aside: this video had a lot of text displayed in the video itself; I think a cool feature of `auto-subtitle` would be to "enhance" the language model by favoring words/spellings that appear in the video&mdash;this would have detected "bourrée" and "gigue".)

3. This was more in other videos I tested, but sometimes the timings were off a little bit. This happened most when there were vacant stretches of noise or silence.

I went ahead and fixed these small mistakes in my text editor. SRT also supports a handful of HTML-like markup tags. So for instance, I was able to italicize _basso continuo_ by tagging it like `<i>basso continuo</i>`. You can also change font color like `<font color="green">...</font>`.

## Step 3: Recombine SRT with video

The last step is to combine the fixed-up SRT file with the original video. For this I used the venerable [ffmpeg](http://ffmpeg.org) library, like so:

```plaintext
ffmpeg -i video.mp4 -vf subtitles=caption/video.srt caption/video.final.mp4
```

(__NOTE__: make sure to input the original video, _not_ the already-captioned one, since by default it will overlay the new captions on top of the old ones, which is not what you want.)

If you don't like the default appearance of the captions, you can control various things like font size and position using the `force_style` option.

### Digression: on efficiency

While I do love `ffmpeg` (and so does [this guy](https://www.youtube.com/watch?v=9kaIXkImCAM)), there is a downside to this approach compared to a proper subtitle editor, which is that you don't get instant feedback. Whenever you want to make a new change to the captions, you have to re-merge them with the video, which can take some time. In my case, I was just fixing up some typos, so this approach worked just fine.

However, there's another way to do this using a "softsub" instead of a "hardsub." Certain formats like MKV support captions natively, and it's much less work for `ffmpeg` to simply "embed" the captions into the file rather than "burning it into" the video itself. Here's an example of how to do this:

```plaintext
ffmpeg -i video.mp4 -i caption/video.srt -codec copy -map 0 -map 1 caption/video.softsub.mkv
```

Note this will not work if you set the output extension to `.mp4` because that format does not support softsubs.

On my test video, the softsub command took 0.1 seconds to run, compared to 24 seconds for the hardsub&mdash;over 200 times faster!

You can open MKV files in most media players. I used VLC, but one pitfall I had was that the captions didn't show up immediately; I had to activate Track 1 in the Subtitle menu first.

The method above does not seem to let you set formatting options for the captions, but there are other ways to do it. One such way is to convert the SRT into an ASS file (yes, you heard me... an [ASS](https://fileformats.fandom.com/wiki/SubStation_Alpha) file).

```bash
ffmpeg -i caption/video.srt caption/video.ass
```

This file contains some header data that lets you control the styles. You can then merge the ASS 🍑 into your video using the same `ffmpeg` command as before.

That said, the ASS format and others like it seem much more complicated to work with than SRT; at that point you may be better off just using a graphical subtitle editor.

## Conclusion

The subtitled version of my test video, following the procedures above, can be found [here](https://www.youtube.com/watch?v=89Jy7EZQrzs). You can learn a thing or two about my favorite musical genre. 😉🎶

Anyway, I found this whole exercise to be pretty eye-opening, and it shows how easy it is to put high-quality captions on your videos without breaking the bank. I hope this explainer has been useful to you!
