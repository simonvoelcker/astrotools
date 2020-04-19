import React, { Component } from 'react'
import GlowAsset from '../../assets/img/glow.png'
import { AppConsumer } from '../../context/AppContext'

export default class CircularProgressIndicator extends Component {
  constructor (props) {
    super(props)

    this.options = {
      color: 'rgb(0,205,250)',
      strokeWidth: 1.3,
      radius: 94,
      printerStatesLables: [
        { label: 'Bed preparation', x: 'calc(50% + 1em)', y: '-1em' },
        { label: 'Heat up', x: 'calc(73.23% + 1em)', y: 'calc(8% - 1em)' },
        { label: 'Print', x: 'calc(43.23% + 1em)', y: 'calc(96.77% + 1em)' },
        { label: 'Cool down', x: 'calc(5% -1em)', y: 'calc(13.65% - 1em)' },
        { label: 'Remove', x: 'calc(33% - 1em)', y: '-1em' }
      ]
    }

    this.getPathLength = () => {
      return this.options.radius * Math.PI
    }

    this.dashArray = () => {
      let pathLength = this.getPathLength()
      let gap = pathLength * 0.01
      return [
        pathLength * 0.06 - gap,
        gap,
        pathLength * 0.06 - gap,
        gap,
        pathLength * 0.74 - gap,
        gap,
        pathLength * 0.07 - gap,
        gap,
        pathLength * 0.07 - gap,
        gap
      ]
    }
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div className='panel-circularprogressindicator'>
            <div className='progress-shadow'><img alt={'glow'} src={GlowAsset} /></div>
            <ul className='printer-states'>
              {this.options.printerStatesLables.map(({ x, y, label }, index) => {
                return (
                  <li
                    key={index}
                    className='spitzmarke'
                    style={{ top: y, left: x }}
                  >
                    {label}
                  </li>

                )
              })}
            </ul>
            <svg viewBox='0 0 100 100' style={{ display: 'block', width: '100%' }}>
              <path
                d='M 50,50 m 0,-47 a 47,47 0 1 1 0,94 a 47,47 0 1 1 0,-94'
                stroke={this.options.color}
                strokeWidth={this.options.strokeWidth - 0.1}
                fillOpacity='0'
                style={{ strokeDasharray: this.dashArray(), strokeDashoffset: 0 }}
              />
              <path
                className='progress-indicator' d='M 50,50 m 0,-47 a 47,47 0 1 1 0,94 a 47,47 0 1 1 0,-94'
                stroke='rgba(0,0,0,0.7)'
                strokeWidth={this.options.strokeWidth}
                fillOpacity='0'
                style={{
                  strokeDasharray: [this.getPathLength(), this.getPathLength()],
                  strokeDashoffset: this.getPathLength() * (store.totalPrintProgress ? store.totalPrintProgress : 0) * -1
                }}
              />
            </svg >
          </div >
        )}
      </AppConsumer>
    )
  }
}
