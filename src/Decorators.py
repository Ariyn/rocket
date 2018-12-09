def Args(argType=None):
	def _(f):
		if not hasattr(f, "args"):
			setattr(f, "args", [])
		f.args.append(argType)

		return f
	return _

def On(activeName):
	def _(f):
		def __(self, *args, **kwargs):
			self.isActive[activeName] = True

			args = [self]+[kwargs[i] for i in f.args if i in kwargs]
			ret = f(*args)

			return self.isActive[activeName]

		setattr(__, "__OriginalFunc__", f)
		setattr(__, "__ActiveName__", activeName)
		setattr(__, "args", f.args)
		return __

	return _

def Off(activeName):
	def _(f):
		def __(self, *args, **kwargs):

			self.isActive[activeName] = False

			args = [self]+[kwargs[i] for i in f.args if i in kwargs]
			ret = f(*args)

			return self.isActive[activeName]

		setattr(__, "__OriginalFunc__", f)
		setattr(__, "__ActiveName__", activeName)
		setattr(__, "args", f.args)
		return __

	return _

def Toggle(activeName):
	def _(f):
		def __(self, *args, **kwargs):
			self.isActive[activeName] = not self.isActive[activeName]
			# print(activeName, self.isActive[activeName])
			args = {"self":self}

			args.update({i:kwargs[i] for i in f.args if i in kwargs})
			ret = f(**args)

			return self.isActive[activeName]

		setattr(__, "__OriginalFunc__", f)
		setattr(__, "__ActiveName__", activeName)
		setattr(__, "args", f.args)
		return __

	return _

def ActionablePart(cls):
	cls.isActive = {}

	for i in dir(cls):
		if i[:1] != "__":
			func = getattr(cls, i)
			if hasattr(func, "__ActiveName__"):
				__ActiveName__ = getattr(func, "__ActiveName__")
				cls.isActive[__ActiveName__] = False

	return cls

def Snapshot(cls):
	pass
