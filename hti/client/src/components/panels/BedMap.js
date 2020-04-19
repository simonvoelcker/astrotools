import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import SpinnerButton from '../panels/SpinnerButton'
import { formatTemperature } from '../../Utils.js'

export default class BedMap extends Component {
  componentDidMount () {
    this.context.mutations.getBedMap()
  }

  canSetTemperature () {
    let store = this.context.store
    return (
      store.temperatures.rBed !== 80.0 &&
      !store.printingNow &&
      !store.runningCommand &&
      !store.pendingRequest &&
      store.mode !== 'demo'
    )
  }

  canRunBedMapping () {
    let store = this.context.store
    return (
      !store.printingNow &&
      !store.runningCommand &&
      !store.pendingRequest &&
      !store.doorStatus.doorOpen &&
      store.machineHomed &&
      store.mode !== 'demo'
    )
  }

  render () {
    const actualBedTemperature = formatTemperature(this.context.store.temperatures.arBed)

    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div style={{ marginBottom: '52px' }}>
            <div>Bed Map Delta Value<span style={{ fontSize: '28px', marginLeft: '130px' }}>{!isNaN(store.bedMapDelta) ? store.bedMapDelta.toFixed(3) : ''}</span></div>
            <button
              className='btn'
              style={{ display: 'block' }}
              disabled={!this.canSetTemperature()}
              onContextMenu={(e) => e.preventDefault()}
              onClick={() => { mutations.setTemperature('Bed', 80) }}>{'Heat Bed: 80°C (' + actualBedTemperature + '°C)'}
            </button>
            <SpinnerButton
              datacy='StartBedMapping'
              disabled={!this.canRunBedMapping()}
              onClick={() => { mutations.runCommand(store.hmiCommands.bedLevelling) }}
              request={store.hmiCommands.bedLevelling.id}>
              Start Bed Mapping
            </SpinnerButton>
            <div className='bed-map' data-cy='BedMap' style={{ height: '346px' }}>
              <div className='bed-map-rows'>
                {store.bedMapPoints.slice(7, 10).map((point, index) => {
                  return (
                    <div data-cy='bedpoint' key={index}>
                      <h2>{point.toFixed(3)}</h2>
                    </div>
                  )
                })}
              </div>
              <div className='bed-map-rows'>
                {store.bedMapPoints.slice(4, 7).reverse().map((point, index) => {
                  return (
                    <div data-cy='bedpoint' key={index}>
                      <h3>{point.toFixed(3)}</h3>
                    </div>
                  )
                })}
              </div>
              <div className='bed-map-rows'>
                {store.bedMapPoints.slice(1, 4).map((point, index) => {
                  return (
                    <div data-cy='bedpoint' key={index}>
                      <h2>{point.toFixed(3)}</h2>
                    </div>
                  )
                })}
              </div>
            </div>
            <p style={{ marginBottom: 0 }}>Negative value: turn counter clockwise to raise bed</p>
            <p>Positive value: turn clockwise to lower bed</p>
          </div>
        )}
      </AppConsumer>
    )
  }
}

BedMap.contextType = AppContext
