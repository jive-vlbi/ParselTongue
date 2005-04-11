import Obit
import OErr, OSystem
import History, UV


def _scalarize(value):
    """Scalarize a value.

    If VALUE is a list that consists of a single element, return that
    element.  Otherwise return VALUE."""

    if type(value) == list and len(value) == 1:
        return value[0]
    return value


def _vectorize(value):
    """Vectorize a value.

    If VALUE is a scalar, return a list consisting of that scalar.
    Otherwise return VALUE."""

    if type (value) != list:
        return [value]
    return value


class _AIPSTableRow:
    """This class is used to access rows in an extension table."""

    def __init__(self, table, fields, rownum, err):
        self._err = err
        self._dirty = False
        self._table = table
        self._fields = fields
        self._rownum = rownum
        if self._rownum >= 0:
            assert(not self._err.isErr)
            self._row = self._table.ReadRow(self._rownum + 1, self._err)
            if not self._row:
                raise IndexError, "list index out of range"
            if self._err.isErr:
                raise RuntimeError
            pass
        return

    def __str__(self):
        return str(self._row)

    def _findattr(self, name):
        """Return the field name corresponding to attribute NAME."""

        if name in self._fields:
            return self._fields[name]
        msg =  "%s instance has no attribute '%s'" % \
              (self.__class__.__name__, name)
        raise AttributeError, msg

    def __getattr__(self, name):
        key = self._findattr(name)
        return _scalarize(self._row[key])

    def __setattr__(self, name, value):
        if name.startswith('_'):
            self.__dict__[name] = value
            return
        key = self._findattr(name)
        self._row[key] = _vectorize(value)
        self._dirty = True

    def update(self):
        """Update this row."""

        if self._dirty:
            assert(not self._err.isErr)
            self._table.WriteRow(self._rownum + 1, self._row, self._err)
            if self._err.isErr:
                raise RuntimeError
            self._dirty = False
            pass
        return


class AIPSTableRow(_AIPSTableRow):
    """This class is used as a template row for an extension table."""

    def __init__(self, table):
        _AIPSTableRow.__init__(self, table._table, table._columns,
                               -1, table._err)
        header = table._table.Desc.Dict
        self._row = {}
        self._row['Table name'] = header['Table name']
        self._row['NumFields'] = len(header['FieldName'])
        desc = zip(header['FieldName'], header['type'], header['repeat'])
        for field, type, repeat in desc:
            if type == 2 or type == 3:
                # Integer.
                self._row[field] = repeat * [0]
            elif type == 9 or type == 10:
                # Floating-point number.
                self._row[field] = repeat * [0.0]
            elif type == 13:
                # String.
                self._row[field] = ''
            else:
                msg =  "Unimplemented type %d for field %s" % (type, field)
                raise AssertionError, msg
            continue
        return

    def update(self):
        # A row instantiated by the This row cannot be updated.
        msg =  "%s instance has no attribute 'update'" % \
              self.__class__.__name__
        raise AttributeError, msg


class _AIPSTableIter(_AIPSTableRow):
    """This class is used as an iterator over rows in an extension
    table."""

    def __init__(self, table, fields, err):
        _AIPSTableRow.__init__(self, table, fields, -1, err)

    def next(self):
        """Return the next row."""

        self._rownum += 1
        assert(not self._err.isErr)
        self._row = self._table.ReadRow(self._rownum + 1, self._err)
        if not self._row:
            self._err.Clear()
            raise StopIteration
        assert(not self._err.isErr)
        return self


class _AIPSTable:
    """This class is used to access extension tables to an AIPS UV
    data set."""

    def __init__(self, data, name, version):
        self._err = OErr.OErr()
        self._table = data.NewTable(3, 'AIPS ' + name, version, self._err)
        self._table.Open(3, self._err)
        if self._err.isErr:
            raise RuntimeError
        header = self._table.Desc.Dict
        self._columns = {}
        for column in header['FieldName']:
            # Convert the AIPS ccolumn names into acceptable Python
            # identifiers.
            key = column.lower()
            key = key.replace(' ', '_')
            key = key.rstrip('.')
            key = key.replace('.', '_')
            self._columns[key] = column
            continue
        self.name = name
        self.version = header['version']
        return

    def close(self):
        """Close this extension table.

        Closing an extension table flushes any changes to the table to
        disk and updates the information in the header of the data
        set."""

        assert(not self._err.isErr)
        self._table.Close(self._err)
        if self._err.isErr:
            raise RuntimeError
        return

    # The following functions make an extension table behave as a list
    # of rows.

    def __getitem__(self, key):
        if key < 0:
            key = len(self) - key
        return _AIPSTableRow(self._table, self._columns, key, self._err)

    def __iter__(self):
        return _AIPSTableIter(self._table, self._columns, self._err)

    def __len__(self):
        return self._table.Desc.Dict['nrow']

    def __setitem__(self, key, row):
        if key < 0:
            key = len(self) - key
        assert(not self._err.isErr)
        self._table.WriteRow(key + 1, row._row, self._err)
        if self._err.isErr:
            raise RuntimeError
        return

    def append(self, row):
        """Append a row to this extension table."""

        assert(not self._err.isErr)
        self._table.WriteRow(len(self) + 1, row._row, self._err)
        if self._err.isErr:
            raise RuntimeError
        return


class _AIPSHistory:
    def __init__(self, data):
        self._err = OErr.OErr()
        self._table = History.History('AIPS HI', data.List, self._err)
        self._table.Open(3, self._err)
        if self._err.isErr:
            raise RuntimeError

    def close(self):
        """Close this history table.

        Closing a history table flushes any changes to the table to
        disk and updates the information in the header of the data
        set."""
        self._table.Close(self._err)
        if self._err.isErr:
            raise RuntimeError
        return

    def __getitem__(self, key):
        rec = self._table.ReadRec(key + 1, self._err)
        if not rec:
            raise IndexError, "list index out of range"
        if self._err.isErr:
            raise RuntimeError
        return rec

    def __setitem__(self, key, rec):
        msg = 'You are not allowed to rewrite history!'
        raise NotImplementedError, msg

    def append(self, rec):
        """Append a record to this history table."""

        assert(not self._err.isErr)
        self._table.WriteRec(0, rec, self._err)
        if self._err.isErr:
            raise RuntimeError
        return


class AIPSUVData:
    """This class is used to access an AIPS UV data set."""

    def __init__(self, name, klass, disk, seq):
        self._err = OErr.OErr()
        self._data = UV.newPAUV(name, name, klass, disk, seq, True, self._err)
        if self._err.isErr:
            raise RuntimeError
        return

    _antennas = []
    def _generate_antennas(self):
        """Generate the 'antennas' attribute."""

        if not self._antennas:
            antable = self.table('AN', 0)
            for antenna in antable:
                self._antennas.append(antenna.anname.rstrip())
                continue
            pass
        return self._antennas

    antennas = property(_generate_antennas,
                        doc = 'Antennas in this data set.')

    _polarizations = []
    def _generate_polarizations(self):
        """Generate the 'polarizations' attribute.

        Returns a list of the polarizations for this data set."""

        if not self._polarizations:
            for stokes in self.stokes:
                if len(stokes) == 2:
                    for polarization in stokes:
                        if not polarization in self._polarizations:
                            self._polarizations.append(polarization)
                            pass
                        continue
                    pass
                continue
            pass
        return self._polarizations
    polarizations = property(_generate_polarizations,
                             doc='Polarizations in this data set.')

    _sources = []
    def _generate_sources(self):
        """Generate the 'sources' attribute."""

        if not self._sources:
            sutable = self.table('SU', 0)
            for source in sutable:
                self._sources.append(source.source.rstrip())
                continue
            pass
        return self._sources
    sources = property(_generate_sources,
                       doc='Sources in this data set.')

    _stokes = []
    def _generate_stokes(self):
        """Generate the 'stokes' attribute."""

        stokes_dict = {1: 'I', 2: 'Q', 3: 'U', 4: 'V',
                       -1: 'RR', -2: 'LL', -3: 'RL', -4: 'LR',
                       -5: 'XX', -6: 'YY', -7: 'XY', -8: 'YX'}

        if not self._stokes:
            header = self._data.Desc.Dict
            jlocs = header['jlocs']
            cval = header['crval'][jlocs]
            for i in xrange(header['inaxes'][jlocs]):
                self._stokes.append(stokes_dict[int(cval)])
                cval += header['cdelt'][jlocs]
                continue
            pass
        return self._stokes
    stokes = property(_generate_stokes,
                      doc='Stokes parameters for this data set.')

    def table(self, name, version):
        """Access an extension table attached to this UV data set.

        Returns version VERSION of the extension table NAME.  If
        VERSION is 0, this returns the highest available version of
        the requested extension table."""

        return _AIPSTable(self._data, name, version)

    def attach_table(self, name, version, **kwds):
        """Attach an extension table to this UV data set.

        A new extension table is created if the extension table NAME
        with version VERSION doesn't exist.  If VERSION is 0, a new
        extension table is created with a version that is one higher
        than the highest available version."""

        if version == 0:
            version = Obit.UVGetHighVer(self._data.me, 'AIPS ' + name) + 1

        header = self._data.Desc.Dict
        jlocif = header['jlocif']
        no_if = header['inaxes'][jlocif]
        no_pol = len(self.polarizations)
        if name == 'CL':
            Obit.newUVTableCL(self._data.me, 3, 'AIPS ' + name, [version],
                              no_pol, no_if, kwds['no_term'], self._err.me)
        elif name == 'SN':
            Obit.newUVTableSN(self._data.me, 3, 'AIPS ' + name, [version],
                              no_pol, no_if, self._err.me)
        else:
            raise RuntimeError
        if self._err.isErr:
            raise RuntimeError
        return _AIPSTable(self._data, name, version)

    def zap_table(self, name, version):
        """Remove an extension table from this UV data set."""

        assert(not self._err.isErr)
        self._data.ZapTable('AIPS + name', version, self._err)
        if self._err.isErr:
            raise RuntimeError
        return

    def history(self):
        return _AIPSHistory(self._data)