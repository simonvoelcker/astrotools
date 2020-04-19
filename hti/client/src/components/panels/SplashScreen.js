import React, { Component } from 'react'
import BigrepVideo from '../../assets/img/bigrep.mp4'

export default class SplashScreen extends Component {
  render () {
    return (
      <video style={{ marginLeft: '32px' }} width='960' height='620' autoPlay loop>
        <source src={BigrepVideo} type='video/mp4' />
        Your browser does not support the video tag.
      </video>
    )
  }
}
