// Adds existing functions/methods to DataHarminizer.
export default {
  /**
   * Download grid mapped to NML_LIMS format.
   * @param {String} baseName Basename of downloaded file.
   * @param {Object} dh.hot Handonstable grid instance.
   * @param {Object} data See `data.js`.
   * @param {Object} xlsx SheetJS variable.
   */
  PCGL: {
    fileType: 'tsv',
    status: 'published',
    method: function (dh) {
      // Create an export table with template's headers (2nd row) and remaining rows of data

      const sourceFields = dh.getFields(dh.table);
      const aliases = sourceFields.map(obj => obj.alias);
      const outputMatrix=[aliases]


      console.log(sourceFields)
      console.log(sourceFields[0])
      console.log(sourceFields[0]['exportField']['BeaconV2'][0]['field'])
      console.log(aliases)

      for (const inputRow of dh.getTrimmedData(dh.hot)) {
        const outputRow = [];
        for (const value of inputRow) {
          outputRow.push(value)
        };
        outputMatrix.push(outputRow)
      };
      return outputMatrix;
    },
  },
  'mCODE.STU3': {
    fileType: 'tsv',
    status: 'published',
    method: function (dh) {
      // Create an export table with template's headers (2nd row) and remaining rows of data

      const sourceFields = dh.getFields(dh.table);
      const exportMapping='mCODE.STU3'
      const aliases = sourceFields.map(obj => {
        if (obj.exportField && obj.exportField[exportMapping] && obj.exportField[exportMapping][0] && obj.exportField[exportMapping][0].field) {
          return obj.exportField[exportMapping][0].field;
        } else {
          return obj.alias;
        }
      });
      //const aliases = sourceFields.map(obj => obj.alias);
      const outputMatrix=[aliases]
      console.log(aliases)
      for (const inputRow of dh.getTrimmedData(dh.hot)) {
        const outputRow = [];
        for (const value of inputRow) {
          outputRow.push(value)
        };
        outputMatrix.push(outputRow)
      };
      return outputMatrix;
    }
  },
  'mCODE.STU1': {
    fileType: 'tsv',
    status: 'published',
    method: function (dh) {
      // Create an export table with template's headers (2nd row) and remaining rows of data

      const sourceFields = dh.getFields(dh.table);
      const exportMapping='mCODE.STU1'
      const aliases = sourceFields.map(obj => {
        if (obj.exportField && obj.exportField[exportMapping] && obj.exportField[exportMapping][0] && obj.exportField[exportMapping][0].field) {
          return obj.exportField[exportMapping][0].field;
        } else {
          return obj.alias;
        }
      });
      //const aliases = sourceFields.map(obj => obj.alias);
      const outputMatrix=[aliases]
      console.log(aliases)
      for (const inputRow of dh.getTrimmedData(dh.hot)) {
        const outputRow = [];
        for (const value of inputRow) {
          outputRow.push(value)
        };
        outputMatrix.push(outputRow)
      };
      return outputMatrix;
    }
  },
  'mCODE.STU2': {
    fileType: 'tsv',
    status: 'published',
    method: function (dh) {
      // Create an export table with template's headers (2nd row) and remaining rows of data

      const sourceFields = dh.getFields(dh.table);
      const exportMapping='mCODE.STU2'
      const aliases = sourceFields.map(obj => {
        if (obj.exportField && obj.exportField[exportMapping] && obj.exportField[exportMapping][0] && obj.exportField[exportMapping][0].field) {
          return obj.exportField[exportMapping][0].field;
        } else {
          return obj.alias;
        }
      });
      //const aliases = sourceFields.map(obj => obj.alias);
      const outputMatrix=[aliases]
      console.log(aliases)
      for (const inputRow of dh.getTrimmedData(dh.hot)) {
        const outputRow = [];
        for (const value of inputRow) {
          outputRow.push(value)
        };
        outputMatrix.push(outputRow)
      };
      return outputMatrix;
    }
  },
  'mCODE.STU4': {
    fileType: 'tsv',
    status: 'published',
    method: function (dh) {
      // Create an export table with template's headers (2nd row) and remaining rows of data

      const sourceFields = dh.getFields(dh.table);
      const exportMapping='mCODE.STU4'
      const aliases = sourceFields.map(obj => {
        if (obj.exportField && obj.exportField[exportMapping] && obj.exportField[exportMapping][0] && obj.exportField[exportMapping][0].field) {
          return obj.exportField[exportMapping][0].field;
        } else {
          return obj.alias;
        }
      });
      //const aliases = sourceFields.map(obj => obj.alias);
      const outputMatrix=[aliases]
      console.log(aliases)
      for (const inputRow of dh.getTrimmedData(dh.hot)) {
        const outputRow = [];
        for (const value of inputRow) {
          outputRow.push(value)
        };
        outputMatrix.push(outputRow)
      };
      return outputMatrix;
    }
  },
  'Phenopacket': {
    fileType: 'tsv',
    status: 'published',
    method: function (dh) {
      // Create an export table with template's headers (2nd row) and remaining rows of data

      const sourceFields = dh.getFields(dh.table);
      const exportMapping='Phenopacket'
      const aliases = sourceFields.map(obj => {
        if (obj.exportField && obj.exportField[exportMapping] && obj.exportField[exportMapping][0] && obj.exportField[exportMapping][0].field) {
          return obj.exportField[exportMapping][0].field;
        } else {
          return obj.alias;
        }
      });
      //const aliases = sourceFields.map(obj => obj.alias);
      const outputMatrix=[aliases]
      console.log(aliases)
      for (const inputRow of dh.getTrimmedData(dh.hot)) {
        const outputRow = [];
        for (const value of inputRow) {
          outputRow.push(value)
        };
        outputMatrix.push(outputRow)
      };
      return outputMatrix;
    }
  },
  'FHIR': {
    fileType: 'tsv',
    status: 'published',
    method: function (dh) {
      // Create an export table with template's headers (2nd row) and remaining rows of data

      const sourceFields = dh.getFields(dh.table);
      const exportMapping='FHIR'
      const aliases = sourceFields.map(obj => {
        if (obj.exportField && obj.exportField[exportMapping] && obj.exportField[exportMapping][0] && obj.exportField[exportMapping][0].field) {
          return obj.exportField[exportMapping][0].field;
        } else {
          return obj.alias;
        }
      });
      //const aliases = sourceFields.map(obj => obj.alias);
      const outputMatrix=[aliases]
      console.log(aliases)
      for (const inputRow of dh.getTrimmedData(dh.hot)) {
        const outputRow = [];
        for (const value of inputRow) {
          outputRow.push(value)
        };
        outputMatrix.push(outputRow)
      };
      return outputMatrix;
    }
  },
  'CQDG': {
    fileType: 'tsv',
    status: 'published',
    method: function (dh) {
      // Create an export table with template's headers (2nd row) and remaining rows of data

      const sourceFields = dh.getFields(dh.table);
      const exportMapping='CQDG'
      const aliases = sourceFields.map(obj => {
        if (obj.exportField && obj.exportField[exportMapping] && obj.exportField[exportMapping][0] && obj.exportField[exportMapping][0].field) {
          return obj.exportField[exportMapping][0].field;
        } else {
          return obj.alias;
        }
      });
      //const aliases = sourceFields.map(obj => obj.alias);
      const outputMatrix=[aliases]
      console.log(aliases)
      for (const inputRow of dh.getTrimmedData(dh.hot)) {
        const outputRow = [];
        for (const value of inputRow) {
          outputRow.push(value)
        };
        outputMatrix.push(outputRow)
      };
      return outputMatrix;
    }
  },
  'BeaconV2': {
    fileType: 'tsv',
    status: 'published',
    method: function (dh) {
      // Create an export table with template's headers (2nd row) and remaining rows of data

      const sourceFields = dh.getFields(dh.table);
      const exportMapping='BeaconV2'
      const aliases = sourceFields.map(obj => {
        if (obj.exportField && obj.exportField[exportMapping] && obj.exportField[exportMapping][0] && obj.exportField[exportMapping][0].field) {
          return obj.exportField[exportMapping][0].field;
        } else {
          return obj.alias;
        }
      });
      //const aliases = sourceFields.map(obj => obj.alias);
      const outputMatrix=[aliases]
      console.log(aliases)
      for (const inputRow of dh.getTrimmedData(dh.hot)) {
        const outputRow = [];
        for (const value of inputRow) {
          outputRow.push(value)
        };
        outputMatrix.push(outputRow)
      };
      return outputMatrix;
    }
  },

};
