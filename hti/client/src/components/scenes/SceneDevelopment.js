import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import BedMap from '../panels/BedMap'
import ManualAxisControl from '../panels/ManualAxisControl'
import ExtrusionRateControl from '../panels/ExtrusionRateControl'
import StandardButton from '../panels/StandardButton'

export default class SceneDevelopment extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div data-cy='DevelopmentPage' className='scene' style={{ width: '94%' }}>
            <div style={{ display: 'flex', width: '100%', flexDirection: 'row', justifyContent: 'space-between' }}>
              <div style={{ width: '50%' }}>
                <ManualAxisControl />
                <div className='panel' style={{ marginRight: 0 }}>
                  <ExtrusionRateControl tool='t0' />
                  <ExtrusionRateControl tool='t1' />

                  { /* The Extruder-Id feature is disabled until we know whether we actually need it */ }
                  { /* <StandardButton */ }
                  { /*   datacy={'showExtruderTypeModal'} */ }
                  { /*   onClick={() => { mutations.toggleModal('showExtruderTypeModal') }}> */ }
                  { /*   Set Extruder Types */ }
                  { /* </StandardButton> */ }

                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <BedMap />
                <StandardButton
                  className='btn'
                  disabled={store.mode === 'demo'}
                  onClick={mutations.exitHmi}
                >Exit Hmi
                </StandardButton>
              </div>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

SceneDevelopment.contextType = AppContext
