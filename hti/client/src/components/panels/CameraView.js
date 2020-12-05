import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class CameraView extends Component {

  render () {
    const endpoint = "http://localhost:5000/api/camera/frames?framePath="

    return (
      <AppConsumer>
        {({ store }) => (
          <div className='panel camera-view-panel'>
            {store.framePath !== null
            ? <img id="camera-image" alt='' src={endpoint + encodeURIComponent(store.framePath)} />
            : <img id="camera-image" alt='' src="https://via.placeholder.com/960x540.png" />
            }
            <svg viewBox="0 0 1920 1080">
              {store.annotations.map(a => (
                <rect x={a.x} y={a.y} width={a.width} height={a.height}
                 style={{ "fill-opacity": "0", "stroke-width": "2", "stroke": "rgb(0,255,0)" }} />
              ))}
            </svg>
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
