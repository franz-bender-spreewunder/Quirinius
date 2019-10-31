from keras.callbacks import ModelCheckpoint

from _NiceLearning.AugmentedGenerator import AugmentedGenerator
from _NiceLearning.IdLoader import IdLoader
from _NiceLearning.MeanReciprocalRank import mar, calculate_mAP
from _NiceLearning.Model import ModelGenerator

data, labels, class_weight = IdLoader.load_ids()

split = int(len(data) * 2 / 3)

training_generator = AugmentedGenerator(data, labels, augment=True, start=0, end=split)
validation_generator = AugmentedGenerator(data, labels,  augment=False, start=split+1, end=len(data))

model = ModelGenerator.generate_model()

# LEARN!

model.summary(line_length=150)

model.compile(
    loss='sparse_categorical_crossentropy', #loss='sparse_categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy'])

file_path = "models/model3-{epoch:02d}-{val_loss:.2f}.h5"

checkpoint = ModelCheckpoint(
    file_path,
    monitor='val_loss',
    verbose=1,
    save_weights_only=False,
    save_best_only=True,
    mode='min')

callbacks_list = [checkpoint]
# Train model on dataset
model.fit_generator(generator=training_generator,
                    validation_data=validation_generator,
                    use_multiprocessing=True,
                    workers=8,
                    epochs=100,
                    callbacks=callbacks_list)#,
                    #class_weight=class_weight)

model.save(file_path)