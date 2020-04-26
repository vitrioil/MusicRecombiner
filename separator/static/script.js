localStorage.clear();

document.addEventListener("DOMContentLoaded", function() {
	addListeners();

	var waves = document.getElementsByClassName("waveform")
	for (wav of waves) {
		name = wav.getAttribute("name");
		dir = wav.getAttribute("dir");

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
						})(wavesurfer);

	document.querySelector("#slider-"+name).oninput = (function(surf) {
						return function() {surf.zoom(this.value);}
						})(wavesurfer);

	document.querySelector("#play-all").onclick = (function(surf) {
						return function() {surf.playPause()}
						})(wavesurfer);

	document.querySelector("#stop-all").onclick = (function(surf) {
						return function() {surf.stop()}
						})(wavesurfer);

	wavesurfer.on("region-click", region => {editAnnotation(region, name)});
	wavesurfer.on("region-update-end", region => {editAnnotation(region, name)});

	var copyForm = document.querySelectorAll("#augment-cop-input-"+name);

	var cButton = document.querySelector("#cop-button-"+name);
	cButton.onclick = (function(surf) {
		return function() {
		var copyStart = document.querySelector("#cop-start-"+name).value;
		var copyEnd = Number(copyStart) + Number(document.querySelector("#end-"+name).value)
						- Number(document.querySelector("#start-"+name).value);
		appendStorage(name, {Copy: {start: newStart, end: newEnd, copyStart: copyStart}})
		surf.regions.add(surf.addRegion({
			start: copyStart,
			end: copyEnd,
			drag: true,
			resize: false,
			color: getCopyColor()
		}))
	}})(wavesurfer);
}

function enableVolumeForm(form) {
	form.classList.add("form-visible");

	form.onsubmit = function(e) {
		e.preventDefault();
		form.classList.remove("form-visible");
	}
}

function editAnnotation(region, name) {
	var form = document.querySelector("#form-"+name)
	form.classList.add("form-visible");

	(form.elements["start-"+name].value = Math.round(region.start * 10) / 10),
	(form.elements["end-"+name].value = Math.round(region.end * 10) / 10);

	form.onsubmit = function(e) {
		newStart = form.elements["start-"+name].value
		newEnd = form.elements["end-"+name].value
		e.preventDefault();
		region.update({
			start: newStart,
			end: newEnd
		});
		form.classList.remove("form-visible");
		newVolume = document.querySelector("#vol-input-slider-"+name).value;
		appendStorage(name, {Volume: {start: newStart, end: newEnd, volume: newVolume}})
	};

	form.onreset = function() {
		form.style.opacity = 0;
		form.dataset.region = null;
	};

	form.dataset.region = region.id;
}

function addListeners() {
	var volume_button = document.querySelector("#radio-Volume");
	var copy_button = document.querySelector("#radio-Copy");

	function flip_visibility(form) {
		if(!form.classList.contains("form-visible")) {
			form.classList.add("form-visible");
		} else {
			form.classList.remove("form-visible");
		}
	}

	function enableAugment(form) {
		document.querySelectorAll(".augment-form-nest-input").forEach(
			(item) => {item.classList.remove("form-visible")}
		);
		console.log(form);
		form.classList.add("form-visible");
	}

	var allAugmentInputs = document.querySelectorAll(".augment-input");
	for(augmentInput of allAugmentInputs) {
		//console.log(augmentInput);
		augmentInput.onclick = (function(scopeAugment) {
			return function () {
			var curId = scopeAugment.getAttribute("id");
			tokens = curId.split('-')
			var name = tokens[tokens.length-1]

			var allButton = document.querySelectorAll("#"+curId+" .augment-radio");
			console.log(curId, name);
			for(button of allButton) {
				//console.log(button);
				button.onclick = (function(scopeButton) {
					return function() {
					var buttonText = scopeButton.getAttribute("id").split('-')[0];
					var cmd = buttonText.toLowerCase().slice(0, 3);
					var form = document.querySelector("#augment-"+cmd+"-input-"+name);
					//console.log(buttonText, cmd, form);
					enableAugment(form);
				}})(button);
			}
		}})(augmentInput);
	}

	var augmentButton = document.querySelector("#augment-final-button");
	augmentButton.onclick = sendAugmentData;
}

function getCopyColor() {
	color = "hsla(0, 0, " + Math.random() + ", 1)";
}

function insertStorage(name, keyValue) {
	localStorage.set(name, keyValue);
}

function appendStorage(name, keyValue) {
	var list = localStorage.getItem(name);
	if (list == null) {
		localStorage.setItem(name, JSON.stringify([keyValue]));
		return;
	}
	list = JSON.parse(list);
	list.push(keyValue);
	localStorage.setItem(name, JSON.stringify(list));
}

function sendAugmentData() {
	var xhr = new XMLHttpRequest();
	var jsonData = {}
	Object.keys(localStorage).forEach(key => {
		jsonData[key] = JSON.parse(localStorage.getItem(key));
	});
	jsonData = JSON.stringify(jsonData);

	xhr.open('POST', '/augment');
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.send(jsonData);

	xhr.onreadystatechange = function() {location.href="/augment";}
}
