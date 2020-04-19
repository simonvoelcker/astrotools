import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { formatTemperature, formatTargetTemperature } from '../../Utils.js'
import StandardButton from '../panels/StandardButton'

export default class BedControls extends Component {
  constructor (props) {
    super(props)
    this.temperatureOff = '0.0'
    this.defaultTemperatureOn = '50.0'
  }

  render () {
    let temperatures = this.context.store.temperatures
    const actualBed = formatTemperature(temperatures.arBed)
    const targetBed = formatTargetTemperature(temperatures.rBed)
    const tempOk = temperatures.bTempOkBed

    let temperatureOn = this.defaultTemperatureOn
    if (this.context.store.machineSettings) {
      temperatureOn = parseFloat(this.context.store.machineSettings.bed_temperature).toFixed(1)
    }

    let errorMessage = 'Please press RESET button'
    if (temperatures.bErrorState.arBed.bErrorMaxDeviation) {
      errorMessage = 'Error : ' + temperatures.bErrorState.arBed.strControlGroupName + ' reports a deviation of ' +
        temperatures.bErrorState.arBed.rTempDev + '+/-°C greater than maximum allowable deviation of ' +
        temperatures.bErrorState.arBed.rDeviationMax + '+/-°C'
    }
    if (temperatures.bErrorState.arBed.bErrorMinNOfSensors) {
      errorMessage = 'Error : ' + temperatures.bErrorState.arBed.strControlGroupName + ' reports a faulty sensor. Please check error logs.'
    }
    if (temperatures.bErrorState.arBed.bErrorTempLimit) {
      errorMessage = 'Error : ' + temperatures.bErrorState.arBed.strControlGroupName + ' is exceeding the temperture saftey limit of ' +
        temperatures.bErrorState.arBed.rTempError + '°C'
    }

    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div className='panel' data-cy='Bed' style={{ height: '190px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <div style={{ display: 'flex' }}>
                <h2 style={{ color: '#00cdff' }}>{targetBed > 0 ? '●' : '○'}</h2>&nbsp;
                <h2>Bed</h2>
              </div>
              <div>{actualBed}°C ({targetBed > 0 ? targetBed + '°C' : 'OFF'})</div>
            </div>
            { tempOk ? (
              <div>
                <StandardButton className='btn'
                  disabled={parseFloat(targetBed) === parseFloat(temperatureOn) || store.runningCommand !== null || store.mode === 'demo'}
                  onClick={() => { mutations.setTemperature('Bed', temperatureOn) }}>{temperatureOn}°C</StandardButton>
                <StandardButton className='btn'
                  disabled={parseFloat(targetBed) === parseFloat(this.temperatureOff) || store.isPaused || store.runningCommand !== null || store.mode === 'demo'}
                  onClick={() => { mutations.setTemperature('Bed', this.temperatureOff) }}>OFF</StandardButton>
              </div>
            ) : (
              <div className='temp-sensor-warning'>{ errorMessage }</div>
            ) }
          </div>
        )}
      </AppConsumer>
    )
  }
}

BedControls.contextType = AppContext
