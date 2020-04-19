import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { formatTemperature, formatTargetTemperature } from '../../Utils.js'
import SpinnerButton from './SpinnerButton'
import StandardButton from '../panels/StandardButton'
import PropTypes from 'prop-types'

export default class ExtruderControl extends Component {
  constructor (props) {
    super(props)
    this.temperatureOff = '0.0'
    this.defaultTemperatureOn = this.props.tool === 't0' ? '240.0' : '200.0'
  }

  render () {
    const toolName = this.props.tool === 't0' ? 'T0' : 'T1'
    const temperatures = this.context.store.temperatures
    const toolIndex = (this.props.tool === 't0' ? 0 : 1)
    const actualTemp = formatTemperature(temperatures.arExtruderAvg[toolIndex])
    const tempOk = this.props.tool === 't0' ? temperatures.bTempOkExt1 : temperatures.bTempOkExt2
    const targetTemp = formatTargetTemperature(this.props.tool === 't0' ? temperatures.arExtruder1 : temperatures.arExtruder2)
    const extrudeCommand = this.props.tool === 't0' ? 'prmExt1' : 'prmExt2'
    const zCalibrationCommand = this.props.tool === 't0' ? 'zCalibExt1' : 'zCalibExt2'
    const dataCy = this.props.tool === 't0' ? 'Extruder1' : 'Extruder2'
    const isResuming = (this.context.store.printingNow && this.context.store.isPaused && this.context.store.isHeatingUp)
    //The Extruder-Id feature is disabled until we know whether we actually need it
    //const extruderTypes = this.context.store.machineInfo.extruderTypes
    //const extruderType = this.props.tool === 't0' ? extruderTypes[0] : extruderTypes[1]
    //const extruderName = extruderType.type !== null ? extruderType.desc : 'Unknown'

    let isOOF = this.props.tool === 't0' ? this.context.store.oofStatus.t0Main : this.context.store.oofStatus.t1Main

    let temperatureOn = this.defaultTemperatureOn

    if (this.context.store.extruderSettingsArray) {
      const exInfo = this.context.store.extruderSettingsArray[toolIndex]
      if (exInfo && exInfo.active) {
        temperatureOn = parseFloat(exInfo.material_temperature).toFixed(1)
      }
    }

    const minExtrusionTemperature = this.props.tool === 't0' ? temperatures.bErrorState.arExtruder[0].rTempMinEx : temperatures.bErrorState.arExtruder[1].rTempMinEx
    const targetSet = targetTemp >= minExtrusionTemperature
    let temperatureStable = false
    if (this.props.tool === 't0') {
      temperatureStable = temperatures.bErrorState.arExtruder[0].bTempSteadyState
    } else {
      temperatureStable = temperatures.bErrorState.arExtruder[1].bTempSteadyState
    }

    let canExtrude = targetSet && temperatureStable

    let errorMessage = 'Please press RESET button'
    if (this.props.tool === 't0') {
      if (temperatures.bErrorState.arExtruder[0].bErrorMaxDeviation) {
        errorMessage = 'Error : ' + temperatures.bErrorState.arExtruder[0].strControlGroupName + ' reports a deviation of ' +
          temperatures.bErrorState.arExtruder[0].rTempDev + '+/-°C greater than maximum allowable deviation of ' +
          temperatures.bErrorState.arExtruder[0].rDeviationMax + '+/-°C'
      }
      if (temperatures.bErrorState.arExtruder[0].bErrorMinNOfSensors) {
        errorMessage = 'Error : ' + temperatures.bErrorState.arExtruder[0].strControlGroupName + ' reports a faulty sensor. Please check error logs.'
      }
      if (temperatures.bErrorState.arExtruder[0].bErrorTempLimit) {
        errorMessage = 'Error : ' + temperatures.bErrorState.arExtruder[0].strControlGroupName + ' is exceeding the temperture saftey limit of ' +
          temperatures.bErrorState.arExtruder[0].rTempError + '°C'
      }
    } else {
      if (temperatures.bErrorState.arExtruder[1].bErrorMaxDeviation) {
        errorMessage = 'Error : ' + temperatures.bErrorState.arExtruder[1].strControlGroupName + ' reports a deviation of ' +
          temperatures.bErrorState.arExtruder[1].rTempDev + '+/-°C greater than maximum allowable deviation of ' +
          temperatures.bErrorState.arExtruder[1].rDeviationMax + '+/-°C'
      }
      if (temperatures.bErrorState.arExtruder[1].bErrorMinNOfSensors) {
        errorMessage = 'Error : ' + temperatures.bErrorState.arExtruder[1].strControlGroupName + ' reports a faulty sensor. Please check error logs.'
      }
      if (temperatures.bErrorState.arExtruder[1].bErrorTempLimit) {
        errorMessage = 'Error : ' + temperatures.bErrorState.arExtruder[1].strControlGroupName + ' is exceeding the temperture saftey limit of ' +
          temperatures.bErrorState.arExtruder[1].rTempError + '°C'
      }
    }

    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div data-cy={dataCy} className='panel' style={{ width: '320px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <div style={{ display: 'flex' }}>
                  <h2 style={{ color: '#00cdff' }}>{targetTemp > 0 ? '●' : '○'}</h2>&nbsp;
                  { /* The Extruder-Id feature is disabled until we know whether we actually need it */ }
                  { /* <h2>{toolName} : {extruderName}</h2> */ }
                  <h2>{toolName}</h2>
                </div>
                <div>{actualTemp}°C ({targetTemp > 0 ? targetTemp + '°C' : 'OFF'})</div>
              </div>
              { tempOk ? (
                <div>
                  <StandardButton
                    disabled={parseFloat(targetTemp) === parseFloat(temperatureOn) || store.runningCommand !== null || store.mode === 'demo' || isResuming}
                    onClick={() => { mutations.setTemperature(toolName, temperatureOn) }}
                  >{temperatureOn}°C</StandardButton>
                  <StandardButton
                    disabled={parseFloat(targetTemp) === parseFloat(this.temperatureOff) || store.runningCommand !== null || store.mode === 'demo' || isResuming}
                    onClick={() => { mutations.setTemperature(toolName, this.temperatureOff) }}>OFF</StandardButton>
                  <SpinnerButton
                    disabled={isOOF || !canExtrude || store.doorStatus.doorOpen || !store.machineHomed || store.mode === 'demo' || isResuming}
                    onClick={() => { mutations.runCommand(store.hmiCommands[extrudeCommand]) }}
                    request={store.hmiCommands[extrudeCommand].id}>
                    EXTRUDE
                  </SpinnerButton>
                  <StandardButton
                    datacy={'ChangeFilamentButton' + dataCy}
                    disabled={ isResuming }
                    onClick={() => { mutations.toggleModal('showChangeFilamentModal' + toolName) }}>
                      Change Material
                  </StandardButton>
                  <SpinnerButton
                    disabled={store.printingNow || store.runningCommand !== null || !store.machineHomed || store.doorStatus.doorOpen || store.mode === 'demo' || isResuming}
                    onClick={() => { mutations.runCommand(store.hmiCommands[zCalibrationCommand]) }}
                    request={store.hmiCommands[zCalibrationCommand].id}>
                    Z Calibration
                  </SpinnerButton>
                </div>
              ) : (
                <div className='temp-sensor-warning'>{ errorMessage }</div>
              ) }
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

ExtruderControl.contextType = AppContext

ExtruderControl.propTypes = {
  tool: PropTypes.string
}
