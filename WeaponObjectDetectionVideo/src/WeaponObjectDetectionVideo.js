import React, { useRef, useEffect, useState } from "react";
import { FaStop } from "react-icons/fa";
import moment from "moment";
import axios from 'axios';
import "./WeaponObjectDetectionVideo.css";

const PUBLISHABLE_ROBOFLOW_API_KEY = "rf_q03fPvZXzYZJzVrJEFbMaSPt1yY2";
const PROJECT_URL = "weapon-detection-3esci";
const MODEL_VERSION = "1";

const WeaponObjectDetectionVideo = (props) => {
  const [modelStatus, setModelStatus] = useState("model not loaded");
  const [modelStatusCss, setModelStatusCss] = useState("removed");
  const [enableCamText, setEnableCamText] = useState("Enable camera to start detection");
  const [disableCamButton, setDisableCamButton] = useState(false);
  const [disableStopButton, setDisableStopButton] = useState(true);
  const [currentCoordinates, setCurrentCoordinates] = useState({ latitude: null, longitude: null });

  const canvasRef = useRef(null);
  const streamSourceRef = useRef(null);
  const videoWidth = 460;
  const videoHeight = 460;

  let model = undefined;
  const detectInterval = useRef(null);

  useEffect(() => {
    loadModel();
    loadingAnimations();
    startSendingCoordinates();
  }, []);

  const loadingAnimations = () => {
    setDisableCamButton(true);
    setModelStatusCss("model-status-loading");
    setModelStatus("Object Detection Loading");
    setTimeout(() => {
      setModelStatusCss("removed");
      setDisableCamButton(false);
    }, 2000);
  };

  const showWebCam = async () => {
    setDisableCamButton(true);

    const camPermissions = await enableCam(true);
    if (camPermissions) {
      if (enableCamText === "Restart Camera and Detection") {
        restartCamDetection();
      }

      await loadModel();
      setModelStatusCss("removed");

      await enableCam();
      setDisableStopButton(false);
      startDetection();
    }
  };

  const restartCamDetection = () => {
    // Add any restart logic here if needed
  };

  const loadModel = async () => {
    await window.roboflow
      .auth({
        publishable_key: PUBLISHABLE_ROBOFLOW_API_KEY,
      })
      .load({
        model: PROJECT_URL,
        version: MODEL_VERSION,
        onMetadata: function (m) {},
      })
      .then((ml) => {
        model = ml;
      });
  };

  const startDetection = () => {
    if (model) {
      detectInterval.current = setInterval(() => {
        detect(model);
      }, 1000);
    }
  };

  const stopDetection = async () => {
    clearInterval(detectInterval.current);
    setTimeout(() => {
      clearCanvas();
    }, 500);
  };

  const clearCanvas = () => {
    canvasRef.current.getContext("2d").clearRect(0, 0, videoWidth, videoHeight);
  };

  const enableCam = (checkCamPermission = false) => {
    const constraints = {
      video: {
        width: videoWidth,
        height: videoHeight,
        facingMode: "environment",
      },
    };

    return navigator.mediaDevices.getUserMedia(constraints).then(
      function (stream) {
        if (checkCamPermission) {
          stream.getVideoTracks().forEach((track) => {
            track.stop();
          });
          return true;
        } else {
          streamSourceRef.current.srcObject = stream;
          streamSourceRef.current.addEventListener("loadeddata", function () {
            return true;
          });
        }
      },
      (error) => {
        setDisableCamButton(true);
        setDisableStopButton(true);
        checkCamPermission && alert("You have to allow camera permissions");
        setEnableCamText("Allow your camera permissions and reload");
        return false;
      },
    );
  };

  const stopCamera = () => {
    if (streamSourceRef.current != null && streamSourceRef.current.srcObject !== null) {
      streamSourceRef.current.srcObject.getVideoTracks().forEach((track) => {
        track.stop();
      });
    }
    stopDetection();
    setEnableCamText("Restart Camera and Detection");
    setDisableCamButton(false);
    setDisableStopButton(true);
  };

  const startSendingCoordinates = () => {
    setInterval(() => {
      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
            setCurrentCoordinates({ latitude, longitude });
            sendCoordinatesToServer(latitude, longitude);
          },
          (error) => {
            console.error("Error getting geolocation:", error);
            sendCoordinatesToServer(null, null);
          }
        );
      } else {
        console.error("Geolocation is not supported by this browser.");
        sendCoordinatesToServer(null, null);
      }
    }, 2000);
  };

  const sendCoordinatesToServer = async (latitude, longitude) => {
    try {
      await axios.post('http://localhost:5000/update_coordinates', { latitude, longitude });
    } catch (error) {
      console.error('Error sending coordinates:', error);
    }
  };

  const notifyWeaponDetection = async () => {
    try {
      const response = await axios.post('http://localhost:5000/weapon_detected', {
        coordinates: currentCoordinates
      });
      console.log('Weapon detection notification sent:', response.data);
    } catch (error) {
      console.error('Error notifying weapon detection:', error);
    }
  };

  const detect = async (model) => {
    if (typeof streamSourceRef.current !== "undefined" && streamSourceRef.current !== null) {
      adjustCanvas(videoWidth, videoHeight);

      const detections = await model.detect(streamSourceRef.current);

      let weaponDetected = false;

      if (detections.length > 0) {
        detections.forEach((el) => {
          if (el.class === "weapon" && el.confidence > 0.6) {
            weaponDetected = true;
          }
        });
      }

      if (weaponDetected) {
        notifyWeaponDetection();
      }

      const ctx = canvasRef.current.getContext("2d");
      drawBoxes(detections, ctx);
    }
  };

  const adjustCanvas = (w, h) => {
    canvasRef.current.width = w * window.devicePixelRatio;
    canvasRef.current.height = h * window.devicePixelRatio;

    canvasRef.current.style.width = w + "px";
    canvasRef.current.style.height = h + "px";

    canvasRef.current
      .getContext("2d")
      .scale(window.devicePixelRatio, window.devicePixelRatio);
  };

  const drawBoxes = (detections, ctx) => {
    detections.forEach((row) => {
      if (true) {
        var temp = row.bbox;
        temp.class = row.class;
        temp.color = row.color;
        temp.confidence = row.confidence;
        row = temp;
      }
      if (row.confidence < 0) return;

      var x = row.x - row.width / 2;
      var y = row.y - row.height / 2;
      var w = row.width;
      var h = row.height;

      ctx.beginPath();
      ctx.lineWidth = 1;
      ctx.strokeStyle = row.color;
      ctx.rect(x, y, w, h);
      ctx.stroke();

      ctx.fillStyle = "black";
      ctx.globalAlpha = 0.2;
      ctx.fillRect(x, y, w, h);
      ctx.globalAlpha = 1.0;

      var fontColor = "black";
      var fontSize = 12;
      ctx.font = `${fontSize}px monospace`;
      ctx.textAlign = "center";
      var classTxt = row.class;

      var confTxt = (row.confidence * 100).toFixed().toString() + "%";
      var msgTxt = classTxt + " " + confTxt;

      const textHeight = fontSize;
      var textWidth = ctx.measureText(msgTxt).width;

      if (textHeight <= h && textWidth <= w) {
        ctx.strokeStyle = row.color;
        ctx.fillStyle = row.color;
        ctx.fillRect(
          x - ctx.lineWidth / 2,
          y - textHeight - ctx.lineWidth,
          textWidth + 2,
          textHeight + 1,
        );
        ctx.stroke();
        ctx.fillStyle = fontColor;
        ctx.fillText(msgTxt, x + textWidth / 2 + 1, y - 1);
      } else {
        textWidth = ctx.measureText(confTxt).width;
        ctx.strokeStyle = row.color;
        ctx.fillStyle = row.color;
        ctx.fillRect(
          x - ctx.lineWidth / 2,
          y - textHeight - ctx.lineWidth,
          textWidth + 2,
          textHeight + 1,
        );
        ctx.stroke();
        ctx.fillStyle = fontColor;
        ctx.fillText(confTxt, x + textWidth / 2 + 1, y - 1);
      }
    });
  };

  return (
    <div className="outer-container">
      <div className="app-container">
        <p className="garbagedemo-testcases">
          tested on: pixel 7 and iphone 11, chrome browser
        </p>

        <div className="container">
          <div className="top-container">
            <div className="top-button-container">
              <button
                onClick={showWebCam}
                disabled={disableCamButton}
                className={disableCamButton ? "cam-button disable-cam-button" : "cam-button"}
              >
                {enableCamText}
              </button>
            </div>
          </div>
          <div className="graphic-display">
            <div className={modelStatusCss}>
              <p>{modelStatus}</p>
            </div>
          </div>
          <div className="video-display-container">
            <div className="video-display-buttons">
              <button
                className={disableStopButton ? "stop-webcam-button disable-cam-button" : "stop-webcam-button"}
                onClick={stopCamera}
                disabled={disableStopButton}
              >
                <FaStop /> Stop Cam
              </button>
            </div>
            <div className="video-display">
              <canvas ref={canvasRef} className="prediction-window" />
              <video
                ref={streamSourceRef}
                autoPlay
                muted
                playsInline
                width={videoWidth}
                height={videoHeight}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WeaponObjectDetectionVideo;