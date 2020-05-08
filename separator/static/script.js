class CommandStore {
	/*
	 * Stores all the augmentation input
	 * from the user.
	 */

	static customStorage = {};

	static addCommand(name, jsonObject) {
		/*
		 * Add command to storage.
		 * Storage will be submitted to flask
		 * server when user clicks on augment.
		 */
		var commandName = jsonObject["commandName"]
		var keyValue = jsonObject[name]
		this.appendStorage(name, commandName, keyValue);
	}

	static initStorage(name) {
		/*
		 * Initialize key with signal names.
		 */
		this.customStorage[name] = {};
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

	static getCommandDetails(name) {
		/*
		 * Get all command details for one
		 * type of signal provided by name.
		 */
		if(typeof this.customStorage[name] == "undefined") {
			return null;
		}

		var commands = this.customStorage[name];
		return commands;
	}

}

function printStorage() {
	/*
	 * Console command to print storage
	 */
	return CommandStore.customStorage;
}

class Command {
	/*
	 * This class deals with retrieval of user
	 * inputs and storing them as object
	 */
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
		/*
		 * Based on the command name
		 * create object of the specific
		 * command
		 */
		if(this.commandName === "vol") {
			//Volume
			return new Volume(this.getVolumeAttributes());
		} else if(this.commandName === "cop") {
			//Copy
			return new Copy(this.getCopyAttributes());
		}
	}

	getVolumeAttributes() {
		/*
		 * Get volume augmentation input
		 */
		var form = document.querySelector("#form-"+this.audioName)
		var newVolume = document.querySelector("#vol-input-slider-"+this.audioName).value;
		var newStart = form.elements["start-"+this.audioName].value;
		var newEnd = form.elements["end-"+this.audioName].value;

		return {start: newStart, end: newEnd, volume: newVolume}
	}

	getCopyAttributes() {
		/*
		 * Get copy augmentation input
		 */
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

	/*
	 * Add custom getCmdAttributes <here>
	 */

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

	static pretty(obj) {
		return {
			"Command": obj.name,
			"Start": obj.start,
			"End": obj.end,
			"Volume": obj.volume + "%"
		};
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

	static pretty(obj) {
		return {
			"Command": obj.name,
			"Start": obj.start,
			"End": obj.end,
			"Copy": obj.copyStart
		};
	}
}

document.addEventListener("DOMContentLoaded", function() {
	//Initialize all listeners
	addListeners();

	var waves = document.getElementsByClassName("waveform")
	for (wav of waves) {
		//For each waveform setup the page
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

		//Object specific listeners
		setValues(wavesurfer, name);
		//Initialize storage for particular signal
		CommandStore.initStorage(name);
		//Load the waveform
		wavesurfer.load(`http://192.168.0.107:5000${dir}/${name}.wav`);

	}
});

function setValues(wavesurfer, name) {

	setPlayButton(wavesurfer, name);

	//Whenever a region is clicked show the form
	wavesurfer.on("region-click", region => {editAnnotation(region, name)});
	wavesurfer.on("region-update-end", region => {editAnnotation(region, name)});

	//Whenever user clicks on add button, store the user input.
	var addCommandButton = document.querySelector("#add-command-"+name);
	addCommandButton.onclick = function() {
		commandListener(wavesurfer, name);
	}

	//Add progress bar before audio is fully loaded
	progressBar(wavesurfer, name);
}

function setPlayButton(wavesurfer, name) {
	/*
	 * Listeners for audio playback across the page
	 */
	document.querySelector("#button-" + name).onclick = (function(surf) {
						return function() {surf.playPause()}
						})(wavesurfer);

	document.querySelector("#button-forward-" + name).onclick = (function(surf) {
						return function() {surf.skipForward()}
						})(wavesurfer);

	document.querySelector("#button-backward-" + name).onclick = (function(surf) {
						return function() {surf.skipBackward()}
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

	document.querySelector("#play-forward-all").onclick = function() {
		document.querySelectorAll(".button-forward-wave").forEach(btn => {btn.click()})
	};

	document.querySelector("#play-backward-all").onclick = function() {
		document.querySelectorAll(".button-backward-wave").forEach(btn => {btn.click()})
	};
}

function progressBar(wavesurfer, name) {
	var progressDiv = document.querySelector('#progress-bar-'+name);
	var progressBar = progressDiv.querySelector('.progress-bar');

	var showProgress = function(percent) {
		progressDiv.style.display = 'block';
		progressBar.style.width = percent + '%';
	};

	var hideProgress = function() {
		progressDiv.style.display = 'none';
	};

	wavesurfer.on('loading', showProgress);
	wavesurfer.on('ready', hideProgress);
	wavesurfer.on('destroy', hideProgress);
	wavesurfer.on('error', hideProgress);
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
	};

	form.onreset = function() {
		form.style.opacity = 0;
		form.dataset.region = null;
	};

	form.dataset.region = region.id;
}

function addListeners() {
	/*
	 * Setup all listeners
	 */

	//Bulma is a pure CSS framework. Hence, custom JS to show file name when user
	//selects a file
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

	function enableAugment(form) {
		/*
		 * Toggle form based on user click
		 */
		document.querySelectorAll(".augment-form-nest-input").forEach(
			(item) => {item.classList.remove("form-visible")}
		);
		form.classList.add("form-visible");
	}

	var allAugmentInputs = document.querySelectorAll(".augment-input");
	for(augmentInput of allAugmentInputs) {
		augmentInput.onclick = (function(scopeAugment) {
			return function () {
			var curId = scopeAugment.getAttribute("id");
			tokens = curId.split('-')
			var name = tokens[tokens.length-1]

			var allButton = document.querySelectorAll("#"+curId+" .augment-radio");
			for(button of allButton) {
				button.onclick = (function(scopeButton) {
					return function() {
					var buttonText = scopeButton.getAttribute("id").split('-')[0];
					var cmd = buttonText.toLowerCase().slice(0, 3);
					var form = document.querySelector("#augment-"+cmd+"-input-"+name);

					enableAugment(form);
				}})(button);
			}
		}})(augmentInput);
	}

	var augmentButton = document.querySelector("#augment-final-button");
	augmentButton.onclick = sendAugmentData;

	var loadOriginalButton = document.querySelector("#reload-original");
	loadOriginalButton.onclick = loadOriginal;

	var uploadButton = document.querySelector("#upload-button");
	if(uploadButton != null) {
		uploadButton.onclick = function() {
			this.classList.add("is-loading");
		};
	}

	//Show modal
	var toggleButton = document.querySelectorAll(".toggle-modal[id^='toggle-modal']");
	toggleButton.forEach(t=> {
		var name = getLastItem(t.getAttribute("id").split('-'));
		t.onclick = function() {
			toggleModalClasses(name);
		};
	});

}

function toggleModalClasses(name) {
	//Retrieve all user commands
	var modal = document.querySelector(".modal");

	var cmdDetails = CommandStore.getCommandDetails(name);
	if(typeof cmdDetails != "null") {
		var detailsList = [];
		for(var cmdName in cmdDetails) {
			var cmd = cmdDetails[cmdName];
			console.log(cmd);
			for(c of cmd) {
				var cPrettyObj = getPrettyCommand(cmdName, c);
				console.log(cPrettyObj);
				detailsList.push(cPrettyObj);
			}
		}
		addTableToModal(detailsList, name);
	}

	if(modal.classList.contains("is-active")) {
		modal.classList.remove('is-active');
	} else {
		modal.classList.add('is-active');
	}
}

function addTableToModal(detailsList, name) {
	//Add table as a child to modal-body
	var modalBody = document.querySelector(".modal-card-body");
	modalBody.innerHTML = "";
	var subtitle = document.createElement("label");
	var subtitleText = name.charAt(0).toUpperCase() + name.substr(1);
	subtitle.innerHTML = subtitleText;
	var table = document.createElement("table");

	for(details of detailsList) {
		var row = document.createElement("tr");
		console.log(details);
		for(key in details) {
			var data = details[key];
			var keyTableData = document.createElement("td");
			var valueTableData = document.createElement("td");
			keyTableData.innerHTML = key;
			valueTableData.innerHTML = data;

			row.appendChild(keyTableData);
			row.appendChild(valueTableData);
		}
		table.appendChild(row);
	}

	if(detailsList.length === 0) {
		var row = document.createElement("tr");
		row.innerHTML = "No Augmentations for " + subtitleText + ". Add augmentations by clicking on a region on the waveform"
		table.appendChild(row);
	} else {
		modalBody.appendChild(subtitle);
	}

	table.className = "table";
	modalBody.appendChild(table);

}

function addTablesToModal(detailsList, name) {
	//Add table as a child to modal-body
	var modalBody = document.querySelector(".modal-card-body");
	modalBody.innerHTML = "";
	var subtitle = document.createElement("label");
	var subtitleText = name.charAt(0).toUpperCase() + name.substr(1);
	subtitle.innerHTML = subtitleText;


	for(table of tables) {
		table.className = "table";
		modalBody.appendChild(table);
	}
}

function getPrettyCommand(cmdName, cmd) {
	if(cmdName === "Copy") {
		return Copy.pretty(cmd);
	} else if(cmdName === "Volume") {
		return Volume.pretty(cmd);
	}
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

