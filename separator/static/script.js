var waves = document.getElementsByClassName("waveform")
for (wav of waves) {
	name = wav.getAttribute("name")
	dir = wav.getAttribute("dir")

	var wavesurfer = WaveSurfer.create({
	    container: "#waveform-" + name,
	    backend: 'MediaElement'
	});

	document.getElementById(`button-${name}`).onclick = (function(surf) {
						return function() {surf.playPause()}
						})(wavesurfer)
	wavesurfer.load(`http://192.168.0.107:5000${dir}/${name}.wav`)
}


