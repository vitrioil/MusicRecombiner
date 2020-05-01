class CommandStore {

	static customStorage = {};

	static addCommand(name, jsonObject) {
		var commandName = jsonObject["commandName"]
		var keyValue = jsonObject[name]
		this.appendStorage(name, commandName, keyValue);
	}

	static initStorage(name) {
		//this.setObject(localStorage, name, {});
		this.customStorage[name] = {};
	}

	static appendObject(driverObject, key, value) {
		var list = this.getObject(driverObject, key);
		list.push(value);
		driverObject.setItem(key, list);
	}

	static setObject(driverObject, key, value) {
		driverObject.setItem(key, value);
	}

	static getObject(driverObject, key) {
		if (typeof driverObject.getItem === "function" && typeof driverObject.getItem(key) != "undefined") {
			return driverObject.getItem(key);
		} else if(typeof driverObject[key] != "undefined") {
			return driverObject[key];
		}
		return null;
	}

	static appendStorage(name, commandName, keyValue) {
		var nameList = this.getObject(this.customStorage, name);
		var commandList = this.getObject(nameList, commandName);

		if (commandList == null) {
			commandList = [];
		}

		commandList.push(keyValue);
		this.customStorage[name][commandName] = commandList;
	}

}

function printStorage() {
	console.log(CommandStore.customStorage);
}

class Command {
	constructor(wavesurfer, audioName) {
		this.wavesurfer = wavesurfer;
		this.audioName = audioName;
		this.getCommandName();
	}

	getCommandName() {
		//get current command selected
		this.commandForm = document.querySelector(".augment-form-nest-input.form-visible[id$="+this.audioName+"]");
		var commandTokens = this.commandForm.getAttribute("id").split('-');

		//format == (id=augment-{cmdName}-input-{audioName})
		this.commandName = commandTokens[1];

		//after knowing the command, get all relevant attributes accordingly
		this.command = this.getCommand();
	}

	getCommand() {
		if(this.commandName === "vol") {
			//Volume
			return new Volume(this.getVolumeAttributes());
		} else if(this.commandName === "cop") {
			//Copy
			return new Copy(this.getCopyAttributes());
		}
	}

	getVolumeAttributes() {
		var form = document.querySelector("#form-"+this.audioName)
		var newVolume = document.querySelector("#vol-input-slider-"+this.audioName).value;
		var newStart = form.elements["start-"+this.audioName].value;
		var newEnd = form.elements["end-"+this.audioName].value;

		return {start: newStart, end: newEnd, volume: newVolume}
	}

	getCopyAttributes() {
		var oldStart = Number(document.querySelector("#start-"+this.audioName).value);
		var oldEnd = Number(document.querySelector("#end-"+this.audioName).value);
		var copyStart = Number(document.querySelector("#cop-start-"+this.audioName).value);

		var copyEnd = copyStart + oldEnd - oldStart
		this.wavesurfer.regions.add(this.wavesurfer.addRegion({
			start: copyStart,
			end: copyEnd,
			drag: false,
			resize: false,
			color: getCopyColor()
		}));

		return {start: oldStart, end: oldEnd, copyStart: copyStart}
	}

	getObject() {
		var jsonObject = {};
		jsonObject[this.audioName] = this.command;
		jsonObject["commandName"] = this.command.name;
		return jsonObject;
	}
}

class Volume {
	start;
	end;
	volume;
	name="Volume";

	constructor(attr) {
		this.start = attr["start"];
		this.end = attr["end"];
		this.volume = attr["volume"];
	}
}

class Copy {
	start;
	end;
	copyStart;
	name="Copy";

	constructor(attr) {
		this.start = attr["start"];
		this.end = attr["end"];
		this.copyStart = attr["copyStart"];
	}
}

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
		CommandStore.initStorage(name);
		wavesurfer.load(`http://192.168.0.107:5000${dir}/${name}.wav`);

	}
});

function setValues(wavesurfer, name) {

	document.querySelector("#button-" + name).onclick = (function(surf) {
						return function() {surf.playPause()}
						})(wavesurfer);

	document.querySelector("#button-stop-" + name).onclick = (function(surf) {
						return function() {surf.stop()}
						})(wavesurfer);

	document.querySelector("#slider-"+name).oninput = (function(surf) {
						return function() {surf.zoom(this.value);}
						})(wavesurfer);

	document.querySelector("#play-all").onclick = function() {
		document.querySelectorAll(".button-play-wave").forEach(btn => {btn.click()})
	};

	document.querySelector("#stop-all").onclick = function() {
		document.querySelectorAll(".button-stop-wave").forEach(btn => {btn.click()})
	};

	wavesurfer.on("region-click", region => {editAnnotation(region, name)});
	wavesurfer.on("region-update-end", region => {editAnnotation(region, name)});

	var addCommandButton = document.querySelector("#add-command-"+name);
	addCommandButton.onclick = function() {
		commandListener(wavesurfer, name);
	}

	/*
	var copyForm = document.querySelectorAll("#augment-cop-input-"+name);

	var cButton = document.querySelector("#cop-button-"+name);
	if (cButton != null) {
		cButton.onclick = (function(surf) {
			return function() {
			var oldStart = Number(document.querySelector("#start-"+name).value);
			var oldEnd = Number(document.querySelector("#end-"+name).value);
			var copyStart = document.querySelector("#cop-start-"+name).value;
			var copyEnd = Number(copyStart) + oldEnd - oldStart
			appendStorage(name, {Copy: {start: oldStart, end: oldEnd, copyStart: copyStart}})
			surf.regions.add(surf.addRegion({
				start: copyStart,
				end: copyEnd,
				drag: false,
				resize: false,
				color: getCopyColor()
			}))
		}})(wavesurfer);
	}*/
}

function commandListener(wavesurfer, audioName) {
	var command = new Command(wavesurfer, audioName);
	var jsonCommand = command.getObject();
	console.log(jsonCommand);
	CommandStore.addCommand(audioName, jsonCommand);
}

function editAnnotation(region, name) {
	var form = document.querySelector("#form-"+name)
	form.classList.add("form-visible-flex");
	//form.classList.add("tile");

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
		form.classList.remove("form-visible-flex");
		//form.classList.remove("tile");
		//newVolume = document.querySelector("#vol-input-slider-"+name).value;
		//appendStorage(name, {Volume: {start: newStart, end: newEnd, volume: newVolume}})
	};

	form.onreset = function() {
		form.style.opacity = 0;
		form.dataset.region = null;
	};

	form.dataset.region = region.id;
}

function addListeners() {
	const fileInput = document.querySelector('#file-input-upload input[type=file]');
	if(fileInput != null) {
		fileInput.onchange = () => {
			if (fileInput.files.length > 0) {
				const fileName = document.querySelector('#file-input-upload .file-name');
				fileName.textContent = fileInput.files[0].name;
			}
		}
	}

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
			//console.log(curId, name);
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

	var loadOriginalButton = document.querySelector("#reload-original");
	loadOriginalButton.onclick = loadOriginal;

}

function getCopyColor() {
	color = "hsla(0, 0, " + Math.random() + ", 1)";
}

function sendAugmentData() {
	var xhr = new XMLHttpRequest();
	jsonData = JSON.stringify(CommandStore.customStorage);

	xhr.open('POST', '/augment');
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.send(jsonData);

	xhr.onreadystatechange = function() {location.href="/augment";}
}

function loadOriginal() {
	const target = new URL(location.href);
	const params = new URLSearchParams();

	params.set("augment", false);
	target.search = params.toString();

	var xhr = new XMLHttpRequest();

	xhr.open('GET', target.href);
	xhr.onreadystatechange = function() {location.href=target.href;}
	xhr.send(null);

}

function getLastItem(arr) {
	len = arr.length;
	return arr[len-1];
}
