document.addEventListener("DOMContentLoaded", function() {

	var waves = document.getElementsByClassName("waveform")
	for (wav of waves) {
		name = wav.getAttribute("name")
		dir = wav.getAttribute("dir")

		var wavesurfer = WaveSurfer.create({
		    container: "#waveform-" + name,
		    plugins: [
			
			WaveSurfer.regions.create({
			    regions: [
				{
				    start: 1,
				    end: 3,
				    loop: false,
				    color: 'hsla(400, 100%, 30%, 0.5)',
				    drag: true,
				    resize: true
				}
			    ],
			    dragSelection: {
				slop: 5
			    }
			}),
			
			WaveSurfer.timeline.create({
                		container: '#wave-timeline-' + name
	            	})
		]
		});

		setValues(wavesurfer, name);	
		wavesurfer.load(`http://192.168.0.107:5000${dir}/${name}.wav`);

	}
});

function setValues(wavesurfer, name) {

	document.querySelector("#button-" + name).onclick = (function(surf) {
						return function() {surf.playPause()}
						})(wavesurfer)

	document.querySelector("#slider-"+name).oninput = (function(surf) {
						return function() {surf.zoom(this.value);}
						})(wavesurfer)

	//document.querySelector("#play-all").onclick = (function(surf) {
	//					return function() {surf.playPause()}
	//					})(wavesurfer)

	//document.querySelector("#stop-all").onclick = (function(surf) {
	//					return function() {surf.stop()}
	//					})(wavesurfer)

	wavesurfer.on("region-click", region => {editAnnotation(region, document.querySelector("#form-"+name))})
	wavesurfer.on("region-update-end", region => {editAnnotation(region, document.querySelector("#form-"+name))})
}

function editAnnotation(region, form) {

    form.classList.add("form-visible");
    
    (form.elements.start.value = Math.round(region.start * 10) / 10),
        (form.elements.end.value = Math.round(region.end * 10) / 10);

    form.onsubmit = function(e) {
        e.preventDefault();
        region.update({
            start: form.elements.start.value,
            end: form.elements.end.value,
        });
	form.classList.remove("form-visible");
    };

    form.onreset = function() {
        form.style.opacity = 0;
        form.dataset.region = null;
    };

    form.dataset.region = region.id;
}

